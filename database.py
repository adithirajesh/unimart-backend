from flask_sqlalchemy import SQLAlchemy
import os 

db = SQLAlchemy()

def init_db(app):
    from models import User, Product, UserActivity  # import models here
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()  # <- This creates tables in Postgres
