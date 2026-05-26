from flask import Blueprint, request, jsonify, session
from models.user import User
from models.system_config import (
    db, FeatureFlag, PlanConfig, ModelCatalog, ResolutionConfig, DurationTier
)

admin_config_bp = Blueprint("admin_config", __name__)


def require_admin():
    user_id = session.get("user_id")
    if not user_id:
        return None, jsonify({"error": "Not authenticated"}), 401

    user = User.query.get(user_id)
    if not user or user.role != "admin":
        return None, jsonify({"error": "Admin access required"}), 403

    return user, None, None


@admin_config_bp.route("/config/all", methods=["GET"])
def get_all():
    _, err, code = require_admin()
    if err:
        return err, code

    return jsonify({
        "feature_flags": [f.as_dict() for f in FeatureFlag.query.all()],
        "plans": [p.as_dict() for p in PlanConfig.query.all()],
        "models": [m.as_dict() for m in ModelCatalog.query.all()],
        "resolutions": [r.as_dict() for r in ResolutionConfig.query.all()],
        "durations": [d.as_dict() for d in DurationTier.query.all()],
    })


@admin_config_bp.route("/feature/toggle", methods=["POST"])
def toggle_feature():
    _, err, code = require_admin()
    if err:
        return err, code

    data = request.get_json()
    name = data["name"]
    enabled = data["enabled"]

    flag = FeatureFlag.query.filter_by(name=name).first()
    if not flag:
        flag = FeatureFlag(name=name, enabled=enabled)
        db.session.add(flag)
    else:
        flag.enabled = enabled

    db.session.commit()
    return jsonify({"message": f"{name} updated"})


@admin_config_bp.route("/plan/save", methods=["POST"])
def save_plan():
    _, err, code = require_admin()
    if err:
        return err, code

    data = request.get_json()
    name = data["name"]

    plan = PlanConfig.query.filter_by(name=name).first()
    if not plan:
        plan = PlanConfig(name=name)
        db.session.add(plan)

    for key, value in data.items():
        if hasattr(plan, key):
            setattr(plan, key, value)

    db.session.commit()
    return jsonify({"message": f"Plan {name} saved"})


@admin_config_bp.route("/model/save", methods=["POST"])
def save_model():
    _, err, code = require_admin()
    if err:
        return err, code

    data = request.get_json()
    key = data["key"]

    model = ModelCatalog.query.filter_by(key=key).first()
    if not model:
        model = ModelCatalog(key=key)
        db.session.add(model)

    for k, v in data.items():
        if hasattr(model, k):
            setattr(model, k, v)

    db.session.commit()
    return jsonify({"message": f"Model {key} saved"})


@admin_config_bp.route("/resolution/save", methods=["POST"])
def save_resolution():
    _, err, code = require_admin()
    if err:
        return err, code

    data = request.get_json()
    name = data["name"]

    res = ResolutionConfig.query.filter_by(name=name).first()
    if not res:
        res = ResolutionConfig(name=name)
        db.session.add(res)

    for k, v in data.items():
        if hasattr(res, k):
            setattr(res, k, v)

    db.session.commit()
    return jsonify({"message": f"Resolution {name} saved"})


@admin_config_bp.route("/duration/save", methods=["POST"])
def save_duration():
    _, err, code = require_admin()
    if err:
        return err, code

    data = request.get_json()
    name = data["name"]

    tier = DurationTier.query.filter_by(name=name).first()
    if not tier:
        tier = DurationTier(name=name)
        db.session.add(tier)

    for k, v in data.items():
        if hasattr(tier, k):
            setattr(tier, k, v)

    db.session.commit()
    return jsonify({"message": f"Duration {name} saved"})
