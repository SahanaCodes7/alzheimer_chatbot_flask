import json
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify, current_app
from models import db, ScreeningSession
from crypto_utils import AESCipher
from nlp_inference import ClinicalClassifier
from xai import lime_explain
from adaptive_flow import score_response, next_question, aggregate_domain_scores

patient_bp = Blueprint('patient', __name__)
_classifier = None

def init_patient_bp(app):
    global _classifier
    from config import Config
    if not hasattr(app, "_clinical_model_loaded"):
        _classifier = ClinicalClassifier(Config.MODEL_NAME)
        app._clinical_model_loaded = True
        # NEW: make model globally reachable (survives debug reloads)
        if not hasattr(app, "extensions"):
            app.extensions = {}
        app.extensions["clinical_classifier"] = _classifier

    app.register_blueprint(patient_bp, url_prefix='/patient')

@patient_bp.route('/dashboard')
def dashboard():
    if 'uid' not in session or session.get('role') != 'patient':
        return redirect(url_for('auth.login'))
    return render_template('patient_dashboard.html', name=session.get('name'))

@patient_bp.route('/chat')
def chat():
    if 'uid' not in session or session.get('role') != 'patient':
        return redirect(url_for('auth.login'))
    return render_template('chat.html', api_token=session.get('api_token'))

@patient_bp.route('/chat/next', methods=['POST'])
def chat_next():
    if 'uid' not in session:
        return jsonify({"error": "unauth"}), 401
    state = request.json.get('state', {"history": []})
    q = next_question(state['history'], max_per_domain=2)
    if q is None:
        return jsonify({"done": True})
    return jsonify(q)

@patient_bp.route('/chat/answer', methods=['POST'])
def chat_answer():
    if 'uid' not in session:
        return jsonify({"error": "unauth"}), 401
    data = request.json
    q = data['question']
    ans = data['answer']
    s = score_response(q['domain'], ans)
    item = {"qid": q['id'], "question": q['text'], "domain": q['domain'], "answer": ans, "score": s}
    return jsonify(item)

@patient_bp.route('/chat/finish', methods=['POST'])
def chat_finish():
    if 'uid' not in session:
        return jsonify({"error": "unauth"}), 401

    try:
        hist = request.json['history']
        transcript = "\n".join(f"Q: {h['question']}\nA: {h['answer']}" for h in hist)

        # 1) Predict (already working)
        pred = _classifier.predict(transcript)  # label & probs ok
    except Exception as e:
        return jsonify({"error": "prediction_failed", "details": str(e)}), 500

    # 2) Aggregate domain scores (keep lightweight)
    try:
        domains = aggregate_domain_scores(hist)
        print("domains==",domains)
    except Exception as e:
        domains = {}
    
    # 3) Save minimal session first (so you always get a session_id back)
    try:
        sess = ScreeningSession(
            user_id=session['uid'],
            raw_text_enc=transcript,            # temporarily plaintext
            domain_scores_enc=json.dumps(domains),
            risk_score=float(max(pred['probs'])),
            risk_label=pred['label'],
            lime_html_enc=""                    # fill later if LIME succeeds
        )
        db.session.add(sess)
        db.session.commit()
    except Exception as e:
        return jsonify({"error": "db_save_failed", "details": str(e)}), 500

    # 4) Best-effort encryption & LIME (won't block the main success path)
    try:
        aes_key = current_app.config.get('AES256_KEY_B64')
        raw_text = transcript
        dom_json = json.dumps(domains)

        # run LIME and keep a plaintext copy for preview
        try:
            lime_html_plain = lime_explain(_classifier, transcript, num_features=12)
        except Exception as le:
            lime_html_plain = f"LIME unavailable: {le}"

        # build preview **from plaintext** (before any encryption)
        xai_preview = (
            lime_html_plain if isinstance(lime_html_plain, str) and len(lime_html_plain) < 32_000
            else (lime_html_plain[:32_000] + "...(truncated)") if isinstance(lime_html_plain, str)
            else ""
        )

        # now optionally encrypt for storage
        lime_html_store = lime_html_plain
        if aes_key:
            aes = AESCipher(aes_key)
            raw_text = aes.encrypt(transcript.encode())
            dom_json = aes.encrypt(json.dumps(domains).encode())
            lime_html_store = aes.encrypt(lime_html_plain.encode())

        # persist (encrypted or plaintext)
        sess.raw_text_enc = raw_text
        sess.domain_scores_enc = dom_json
        sess.lime_html_enc = lime_html_store
        db.session.commit()

    except Exception:
        # Swallow errors here; session already created
        xai_preview = ""

    return jsonify({
        "risk_label": pred['label'],
        "probs": pred['probs'],
        "session_id": sess.id,
        "xai_preview_html": xai_preview
    })
    
@patient_bp.get('/session/<int:sid>/explain')
def get_explanation(sid):
    if 'uid' not in session or session.get('role') != 'patient':
        return redirect(url_for('auth.login'))

    row = ScreeningSession.query.filter_by(id=sid, user_id=session['uid']).first()
    if not row:
        return "Not found", 404

    html = row.lime_html_enc or ""
    aes_key = current_app.config.get('AES256_KEY_B64')

    try:
        if aes_key and html:
            aes = AESCipher(aes_key)
            html = aes.decrypt(html).decode()
    except Exception as e:
        html = f"<p><em>Explanation unavailable: {e}</em></p>"

    # If LIME previously failed, we may have stored a message like "LIME unavailable: ..."
    if not html:
        html = "<p><em>No explanation available for this session.</em></p>"

    # Return as HTML for direct embedding in an <iframe> or innerHTML
    return html

@patient_bp.route('/history')
def history():
    if 'uid' not in session or session.get('role') != 'patient':
        return redirect(url_for('auth.login'))
    uid = session['uid']
    rows = ScreeningSession.query.filter_by(user_id=uid).order_by(ScreeningSession.created_at.asc()).all()
    series = [{"t": r.created_at.isoformat(), "score": r.risk_score, "label": r.risk_label} for r in rows]
    return render_template('patient_history.html', series=json.dumps(series))
