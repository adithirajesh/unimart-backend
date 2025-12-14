from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import UserActivity
from database import db

activity_bp = Blueprint("activity", __name__)

@activity_bp.route("/", methods=["POST"])
@jwt_required()
def log_activity():
    data = request.json
    user_id = get_jwt_identity()
    product_id = data.get("product_id")
    action = data.get("action")

    new_activity = UserActivity(
        user_id=user_id,
        product_id=product_id,
        action=action
    )
    db.session.add(new_activity)
    db.session.commit()

    return jsonify({"message": "Activity logged"}), 201
