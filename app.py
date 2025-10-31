import os
from flask import Flask,session
from config import Config
from models import db
from auth_routes import auth_bp, bcrypt
from patient_routes import init_patient_bp
from doctor_routes import doctor_bp
from appointment_routes import appt_bp
from flask_jwt_extended import JWTManager

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    # Ensure instance dir exists and DB path is absolute (Windows-friendly)
    os.makedirs(app.instance_path, exist_ok=True)
    uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if uri.startswith("sqlite:///instance/") or uri == "sqlite:///instance/app.db":
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(app.instance_path, "app.db")

    db.init_app(app)
    with app.app_context():
        db.create_all()

    bcrypt.init_app(app)
    JWTManager(app)

    # Blueprints
    app.register_blueprint(auth_bp)
    init_patient_bp(app)  # loads model once and registers /patient
    app.register_blueprint(doctor_bp, url_prefix='/doctor')
    app.register_blueprint(appt_bp)
    @app.context_processor
    def inject_user_nav():
        return {
            "is_authenticated": bool(session.get("uid")),
            "user_role": session.get("role"),
            "user_name": session.get("name"),
        }

    @app.get('/')
    def index():
        return "<h3>Alzheimer’s Screening Chatbot</h3><p><a href='/login'>Login</a> | <a href='/signup'>Sign up</a></p>"

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)