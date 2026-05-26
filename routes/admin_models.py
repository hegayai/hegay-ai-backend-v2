import json
import os
from flask import Blueprint, jsonify, session
from models.user import User

# ⭐ Unique blueprint name (prevents conflicts)
admin_models_bp = Blueprint("admin_models_config", __name__)


# ---------------------------------------------------------
# ⭐ ADMIN AUTH CHECK
# ---------------------------------------------------------
def require_admin():
    """Ensure the user is authenticated and is an admin."""
    user_id = session.get("user_id")

    if not user_id:
        return None, jsonify({"error": "Not authenticated"}), 401

    user = User.query.get(user_id)

    if not user or user.role != "admin":
        return None, jsonify({"error": "Admin access required"}), 403

    return user, None, None


# ---------------------------------------------------------
# ⭐ LOAD MODEL REGISTRY SAFELY
# ---------------------------------------------------------
def load_model_registry():
    """
    Loads config/models.json safely.
    Prevents crashes if file is missing or corrupted.
    """
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(base_dir)
        config_path = os.path.join(project_root, "config", "models.json")

        if not os.path.exists(config_path):
            return {"groups": []}

        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception as e:
        print("Model registry load error:", e)
        return {"groups": []}


# ---------------------------------------------------------
# ⭐ ADMIN: GET MODEL CONFIG
# ---------------------------------------------------------
@admin_models_bp.route("/models/config", methods=["GET"])
def get_models_config():
    """Return sorted model registry for the admin panel."""
    _, err, code = require_admin()
    if err:
        return err, code

    registry = load_model_registry()

    # ⭐ Sort groups alphabetically
    groups = registry.get("groups", [])
    groups = sorted(groups, key=lambda g: g.get("name", "").lower())

    # ⭐ Sort models inside each group
    for group in groups:
        models = group.get("models", [])
        group["models"] = sorted(models, key=lambda m: m.get("name", "").lower())

    registry["groups"] = groups

    return jsonify(registry), 200
