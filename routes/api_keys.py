from flask import Blueprint, jsonify, request, session
from database import db
from models.api_key import ApiKey
from models.user import User
from datetime import datetime
import secrets

api_keys_bp = Blueprint("api_keys_bp", __name__)

# ---------------------------------------------------------
# ADMIN AUTH CHECK
# ---------------------------------------------------------
def require_admin():
    user_id = session.get("user_id")

    if not user_id:
        return None, jsonify({"error": "Not authenticated"}), 401

    user = User.query.get(user_id)

    if not user or user.role != "admin":
        return None, jsonify({"error": "Admin access required"}), 403

    return user, None, None


# ---------------------------------------------------------
# LIST ALL API KEYS
# ---------------------------------------------------------
@api_keys_bp.route("/", methods=["GET"])
def list_api_keys():
    try:
        _, err, code = require_admin()
        if err:
            return err, code

        keys = ApiKey.query.order_by(ApiKey.created_at.desc()).all()

        data = []
        for k in keys:
            created = k.created_at.isoformat() if k.created_at else None
            data.append({
                "id": k.id,
                "key": k.key,
                "user": k.user.email if k.user else None,
                "active": k.active,
                "created_at": created
            })

        return jsonify({"api_keys": data})

    except Exception as e:
        print("List API keys error:", e)
        return jsonify({"error": "Failed to load API keys"}), 500


# ---------------------------------------------------------
# CREATE NEW API KEY
# ---------------------------------------------------------
@api_keys_bp.route("/create", methods=["POST"])
def create_api_key():
    try:
        _, err, code = require_admin()
        if err:
            return err, code

        data = request.json or {}
        user_id = data.get("user_id")

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        new_key = ApiKey(
            key=secrets.token_hex(32),
            user_id=user.id,
            active=True,
            created_at=datetime.utcnow()
        )

        db.session.add(new_key)
        db.session.commit()

        return jsonify({
            "message": "API key created",
            "key": new_key.key
        })

    except Exception as e:
        print("Create API key error:", e)
        return jsonify({"error": "Failed to create API key"}), 500


# ---------------------------------------------------------
# REVOKE API KEY
# ---------------------------------------------------------
@api_keys_bp.route("/<int:key_id>/revoke", methods=["POST"])
def revoke_api_key(key_id):
    try:
        _, err, code = require_admin()
        if err:
            return err, code

        key = ApiKey.query.get(key_id)
        if not key:
            return jsonify({"error": "API key not found"}), 404

        key.active = False
        db.session.commit()

        return jsonify({"message": "API key revoked"})

    except Exception as e:
        print("Revoke API key error:", e)
        return jsonify({"error": "Failed to revoke API key"}), 500
