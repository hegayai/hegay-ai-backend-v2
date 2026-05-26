from flask import Blueprint, jsonify, request
from database import db
from models import User
from datetime import datetime

users_bp = Blueprint("users_bp", __name__)

# ---------------------------------------------------------
# GET ALL USERS
# ---------------------------------------------------------
@users_bp.route("/", methods=["GET"])
def get_users():
    try:
        users = User.query.order_by(User.created_at.desc()).all()

        data = []
        for u in users:
            data.append({
                "id": u.id,
                "email": u.email,
                "role": u.role,
                "created_at": u.created_at.isoformat(),
                "last_login": u.last_login.isoformat() if u.last_login else None
            })

        return jsonify({"users": data})

    except Exception as e:
        print("Get users error:", e)
        return jsonify({"error": "Failed to load users"}), 500


# ---------------------------------------------------------
# GET SINGLE USER
# ---------------------------------------------------------
@users_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None
        })

    except Exception as e:
        print("Get user error:", e)
        return jsonify({"error": "Failed to load user"}), 500


# ---------------------------------------------------------
# UPDATE USER ROLE
# ---------------------------------------------------------
@users_bp.route("/<int:user_id>/role", methods=["PUT"])
def update_role(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        data = request.json
        new_role = data.get("role")

        if not new_role:
            return jsonify({"error": "Role is required"}), 400

        user.role = new_role
        db.session.commit()

        return jsonify({"message": "Role updated successfully"})

    except Exception as e:
        print("Update role error:", e)
        return jsonify({"error": "Failed to update role"}), 500


# ---------------------------------------------------------
# DELETE USER
# ---------------------------------------------------------
@users_bp.route("/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        db.session.delete(user)
        db.session.commit()

        return jsonify({"message": "User deleted successfully"})

    except Exception as e:
        print("Delete user error:", e)
        return jsonify({"error": "Failed to delete user"}), 500
