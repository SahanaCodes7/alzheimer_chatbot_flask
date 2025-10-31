from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token
from models import db, User

bcrypt = Bcrypt()
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email'].lower()
        full_name = request.form.get('full_name', '')
        role = request.form.get('role', 'patient')
        pw = request.form['password']
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return redirect(url_for('auth.signup'))
        user = User(email=email, full_name=full_name, role=role, password_hash=bcrypt.generate_password_hash(pw).decode())
        db.session.add(user)
        db.session.commit()
        flash('Account created. Please login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('signup.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].lower()
        pw = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password_hash, pw):
            session['uid'] = user.id
            session['role'] = user.role
            session['name'] = user.full_name
            token = create_access_token(identity=user.id)
            session['api_token'] = token
            return redirect(url_for('patient.dashboard') if user.role=='patient' else url_for('doctor.dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
