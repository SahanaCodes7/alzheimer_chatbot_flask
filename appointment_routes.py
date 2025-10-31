from flask import Blueprint, render_template, request, session, redirect, url_for, current_app
from models import db, Appointment, User
from crypto_utils import AESCipher

appt_bp = Blueprint('appt', __name__)

@appt_bp.route('/appointments/book', methods=['GET','POST'])
def book():
    if 'uid' not in session:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        doctor_id = int(request.form['doctor_id'])
        slot_iso = request.form['slot_iso']
        notes = request.form.get('notes','')
        aes = AESCipher(current_app.config['AES256_KEY_B64'])
        enc_notes = aes.encrypt(notes.encode()) if notes else None
        ap = Appointment(patient_id=session['uid'], doctor_id=doctor_id, slot_iso=slot_iso, notes_enc=enc_notes)
        db.session.add(ap)
        db.session.commit()
        return redirect(url_for('appt.list_my'))
    doctors = User.query.filter_by(role='doctor').all()
    return render_template('appointment_book.html', doctors=doctors)

@appt_bp.route('/appointments')
def list_my():
    if 'uid' not in session:
        return redirect(url_for('auth.login'))
    uid = session['uid']
    role = session['role']
    if role == 'patient':
        appts = Appointment.query.filter_by(patient_id=uid).order_by(Appointment.slot_iso.asc()).all()
    else:
        appts = Appointment.query.filter_by(doctor_id=uid).order_by(Appointment.slot_iso.asc()).all()
    return render_template('appointment_list.html', appts=appts, role=role)
