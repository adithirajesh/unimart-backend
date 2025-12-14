from flask_sqlalchemy import SQLAlchemy
import os 

db = SQLAlchemy()

def init_db(app):
    DATABASE_URL = os.environ.get("DATABASE_URL") or "sqlite:///unimarket.db"

# For Render Postgres, SQLAlchemy expects psycopg:// -> postgresql://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    if os.environ.get("FLASK_ENV") != "production":
        with app.app_context():
            db.create_all()