from flask import Blueprint, request, jsonify
from database import db
from models import User

auth = Blueprint("auth", __name__)

# -------------------------
# SIGN UP
# -------------------------
@auth.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({"error": "Name and email required"}), 400

    # check if user exists
    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({"error": "Email already registered"}), 400

    new_user = User(name=name, email=email)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "Signup successful",
        "user_id": new_user.id
    }), 200


# -------------------------
# LOGIN
# -------------------------
@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({"error": "Name and email required"}), 400

    user = User.query.filter_by(email=email).first()

    # Auto-create user on first login
    if not user:
        user = User(name=name, email=email)
        db.session.add(user)
        db.session.commit()

    return jsonify({
        "message": "Login successful",
        "user_id": user.id
    }), 200
