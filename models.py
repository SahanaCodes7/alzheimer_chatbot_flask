from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(16), nullable=False, default="patient")
    full_name = db.Column(db.String(120))

class ScreeningSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    raw_text_enc = db.Column(db.Text, nullable=False)
    domain_scores_enc = db.Column(db.Text, nullable=False)
    risk_score = db.Column(db.Float, nullable=False)
    risk_label = db.Column(db.String(32), nullable=False)
    lime_html_enc = db.Column(db.Text)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    slot_iso = db.Column(db.String(64), nullable=False)
    notes_enc = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
