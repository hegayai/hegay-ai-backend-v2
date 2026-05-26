import json
import os
from flask import Blueprint, jsonify, request, session
from database import db
from models.user import User
from models.billing import BillingEvent
from datetime import datetime

credits_engine_bp = Blueprint("credits_engine_bp", __name__)


# ---------------------------------------------------------
# Load model registry from /config/models.json
# ---------------------------------------------------------
def load_model_registry():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    config_path = os.path.join(project_root, "config", "models.json")

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


MODEL_REGISTRY = load_model_registry()


# ---------------------------------------------------------
# Helper: Find model by key
# ---------------------------------------------------------
def find_model(model_key):
    for group in MODEL_REGISTRY["groups"]:
        for model in group["models"]:
            if model["key"] == model_key:
                return model
    return None


# ---------------------------------------------------------
# Helper: Require authentication
# ---------------------------------------------------------
def require_auth():
    user_id = session.get("user_id")
    if not user_id:
        return None, jsonify({"error": "Unauthorized"}), 401

    user = User.query.get(user_id)
    if not user:
        return None, jsonify({"error": "Unauthorized"}), 401

    return user, None, None


# ---------------------------------------------------------
# Billing event logger
# ---------------------------------------------------------
def log_billing_event(user_id, model_key, model_name, credits_used, details=None):
    event = BillingEvent(
        user_id=user_id,
        plan=None,
        category="usage",
        feature=model_key,
        credits_used=credits_used,
        details=details or {},
        created_at=datetime.utcnow(),
    )
    db.session.add(event)


# ---------------------------------------------------------
# Hybrid Credit Calculation
# ---------------------------------------------------------
def calculate_credits(model, tier=None):
    # Fixed cost (Category A)
    if isinstance(model["credits_cost"], int):
        return model["credits_cost"]

    # Hybrid cost (Category B)
    base = model["credits_cost"]["base"]
    tiers = model["credits_cost"].get("tiers", {})

    if tier and tier in tiers:
        return tiers[tier]

    return base


# ---------------------------------------------------------
# Deduct credits endpoint
# ---------------------------------------------------------
@credits_engine_bp.route("/deduct", methods=["POST"])
def deduct_credits():
    user, err, code = require_auth()
    if err:
        return err, code

    data = request.get_json() or {}
    model_key = data.get("model_key")
    tier = data.get("tier")  # optional

    if not model_key:
        return jsonify({"error": "model_key is required"}), 400

    model = find_model(model_key)
    if not model:
        return jsonify({"error": "Unknown model_key"}), 400

    # Admin-only protection
    if model.get("admin_only") and user.role != "admin":
        return jsonify({"error": "This tool is admin-only"}), 403

    # Calculate credits
    credits_needed = calculate_credits(model, tier)

    if user.credits_remaining < credits_needed:
        return jsonify({"error": "Insufficient credits"}), 402

    # Deduct
    user.credits_used += credits_needed

    # Log event
    log_billing_event(
        user_id=user.id,
        model_key=model_key,
        model_name=model["name"],
        credits_used=credits_needed,
        details={
            "tier": tier,
            "gpu_heavy": model.get("gpu_heavy", False),
            "path": model.get("path"),
        },
    )

    db.session.commit()

    return jsonify({
        "success": True,
        "credits_used": credits_needed,
        "credits_remaining": user.credits_remaining,
        "model": model["name"],
        "tier": tier
    })
