import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
    # We'll override this to an absolute path in app.py if it points to instance/
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///instance/app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "58ce1fbedf1b237f12074f19b4b6e5cc5c2dee70eabad70b1c2438bc3f9ac0e2"
    AES256_KEY_B64 = "iWVka3sDLtQbsxiiuXMzNmiyl5Iqugv6yLPvbOge/5E="
    MODEL_NAME = "emilyalsentzer/Bio_ClinicalBERT"
