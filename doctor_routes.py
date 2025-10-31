from flask import Blueprint, render_template, session, redirect, url_for, current_app
from models import db, User, ScreeningSession
from crypto_utils import AESCipher

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/dashboard')
def dashboard():
    if 'uid' not in session or session.get('role') != 'doctor':
        return redirect(url_for('auth.login'))
    patients = User.query.filter_by(role='patient').all()

    aes_key = current_app.config.get('AES256_KEY_B64')  # was [] indexing
    aes = AESCipher(aes_key) if aes_key else None

    latest = []
    for p in patients:
        sess = (ScreeningSession.query
                .filter_by(user_id=p.id)
                .order_by(ScreeningSession.created_at.desc())
                .first())
        if sess:
            html = sess.lime_html_enc or ""
            if aes and html:
                try:
                    html = aes.decrypt(html).decode()
                except Exception as e:
                    html = f"<p><em>Explanation unavailable: {e}</em></p>"
            # if plaintext (no AES key), html already usable
            latest.append({"patient": p, "session": sess, "lime_html": html})

    return render_template('doctor_dashboard.html', latest=latest)