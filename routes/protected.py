from flask import Blueprint, jsonify, session
from models.user import User
from utils.allowances import get_plan_allowances
from utils.video_limits import get_max_video_seconds

protected_bp = Blueprint("protected", __name__)

@protected_bp.route("/me", methods=["GET"])
def me():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Not authenticated"}), 401

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # -----------------------------
        # ⭐ SAFE PLAN ALLOWANCES
        # -----------------------------
        plan = user.plan or "free"
        plan_allowances = get_plan_allowances(plan)

        # -----------------------------
        # ⭐ SAFE VIDEO LIMITS
        # -----------------------------
        max_video_seconds = get_max_video_seconds(user)

        # -----------------------------
        # ⭐ SAFE CREDIT FIELDS
        # -----------------------------
        credits_total = user.credits_total or 0
        credits_used = user.credits_used or 0
        credits_remaining = user.credits_remaining or (credits_total - credits_used)

        # -----------------------------
        # ⭐ SAFE METADATA
        # -----------------------------
        created_at = user.created_at.isoformat() if user.created_at else None
        last_login = user.last_login.isoformat() if user.last_login else None

        return jsonify({
            "id": user.id,
            "email": user.email,
            "name": user.name or None,
            "role": user.role,

            # Category A (subscription)
            "plan": plan,
            "plan_allowances": plan_allowances,
            "max_video_seconds": max_video_seconds,

            # Category B (credits)
            "credits_total": credits_total,
            "credits_used": credits_used,
            "credits_remaining": credits_remaining,

            # Metadata
            "created_at": created_at,
            "last_login": last_login
        }), 200

    except Exception as e:
        print("Protected route error:", e)
        return jsonify({"error": "Server error"}), 500
