import os
from flask import Flask, session
from config import Config
from models import db
from auth_routes import auth_bp, bcrypt
from patient_routes import init_patient_bp
from doctor_routes import doctor_bp
from appointment_routes import appt_bp
from flask_jwt_extended import JWTManager

def create_app():
    # Explicitly set static/templates folders if you have them
    app = Flask(__name__, instance_relative_config=True,
                static_folder="static", template_folder="templates")

    # Prefer environment-provided config (useful on Vercel)
    app.config.from_object(Config)

    # If an external DB is provided via env (recommended for production),
    # use that. Otherwise keep your sqlite fallback but place DB in instance_path.
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        # Accept typical SQLAlchemy URL (postgres:// or postgresql:// etc.)
        app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    else:
        # On serverless platforms like Vercel the project filesystem is mostly read-only.
        # Use /tmp/instance on Vercel so sqlite can be created there (ephemeral).
        if os.environ.get("VERCEL"):
            # Vercel sets the VERCEL env var — write to /tmp (ephemeral)
            instance_dir = "/tmp/instance"
            app.instance_path = instance_dir
        else:
            instance_dir = app.instance_path

        os.makedirs(instance_dir, exist_ok=True)

        # If config used the relative sqlite path, convert it to absolute in instance_dir
        uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
        if uri.startswith("sqlite:///instance/") or uri == "sqlite:///instance/app.db":
            app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(instance_dir, "app.db")

    # Init DB and create tables (if using sqlite or a DB user has access to)
    db.init_app(app)
    with app.app_context():
        try:
            db.create_all()
        except Exception:
            # In production (external DB) migrations are preferred; ignore on init if it fails.
            pass

    bcrypt.init_app(app)
    JWTManager(app)

    # Blueprints
    app.register_blueprint(auth_bp)
    init_patient_bp(app)  # registers /patient
    app.register_blueprint(doctor_bp, url_prefix="/doctor")
    app.register_blueprint(appt_bp)

    @app.context_processor
    def inject_user_nav():
        return {
            "is_authenticated": bool(session.get("uid")),
            "user_role": session.get("role"),
            "user_name": session.get("name"),
        }

    @app.get("/")
    def index():
        return "<h3>Alzheimer’s Screening Chatbot</h3><p><a href='/login'>Login</a> | <a href='/signup'>Sign up</a></p>"

    return app

# create top-level app variable so Vercel (and other WSGI loaders) can import it
# Wrap create_app in try/except so any import/initialization errors are printed to logs.
import traceback, sys

try:
    app = create_app()
except Exception:
    print("===== create_app() failed with exception =====", file=sys.stderr)
    traceback.print_exc()
    # re-raise so Vercel also sees function failure (and you get a 500)
    raise

if __name__ == "__main__":
    # Only use debug locally
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=debug_mode)

