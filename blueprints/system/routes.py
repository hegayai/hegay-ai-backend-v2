from flask import Blueprint, jsonify, request, session
from datetime import datetime
from database import db

system_bp = Blueprint("system", __name__)

# ---------------------------------------------------------
# ⭐ System Settings Model (inline for now)
# ---------------------------------------------------------
class SystemSetting(db.Model):
    __tablename__ = "system_settings"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.JSON, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "key": self.key,
            "value": self.value,
            "updated_at": self.updated_at.isoformat(),
        }


# ---------------------------------------------------------
# ⭐ Helper: Admin check
# ---------------------------------------------------------
def require_admin():
    if "user_id" not in session:
        return False, {"error": "Not logged in"}, 401

    if "admin" not in session.get("roles", []):
        return False, {"error": "Admin access required"}, 403

    return True, None, None


# ---------------------------------------------------------
# ⭐ Get system version
# ---------------------------------------------------------
@system_bp.route("/version", methods=["GET"])
def system_version():
    return jsonify({
        "version": "1.0.0",
        "name": "OS Supreme Backend",
        "timestamp": datetime.utcnow().isoformat()
    }), 200


# ---------------------------------------------------------
# ⭐ Get all system settings (admin only)
# ---------------------------------------------------------
@system_bp.route("/settings", methods=["GET"])
def get_settings():
    ok, err, code = require_admin()
    if not ok:
        return jsonify(err), code

    settings = SystemSetting.query.all()
    return jsonify([s.to_dict() for s in settings]), 200


# ---------------------------------------------------------
# ⭐ Update or create a system setting (admin only)
# ---------------------------------------------------------
@system_bp.route("/settings", methods=["POST"])
def update_setting():
    ok, err, code = require_admin()
    if not ok:
        return jsonify(err), code

    data = request.get_json()
    key = data.get("key")
    value = data.get("value")

    if not key:
        return jsonify({"error": "key required"}), 400

    setting = SystemSetting.query.filter_by(key=key).first()

    if setting:
        setting.value = value
    else:
        setting = SystemSetting(key=key, value=value)
        db.session.add(setting)

    db.session.commit()

    return jsonify({"message": "Setting saved", "setting": setting.to_dict()}), 200


# ---------------------------------------------------------
# ⭐ Maintenance mode toggle (admin only)
# ---------------------------------------------------------
@system_bp.route("/maintenance", methods=["POST"])
def maintenance_mode():
    ok, err, code = require_admin()
    if not ok:
        return jsonify(err), code

    data = request.get_json()
    enabled = data.get("enabled", False)

    setting = SystemSetting.query.filter_by(key="maintenance_mode").first()

    if setting:
        setting.value = {"enabled": enabled}
    else:
        setting = SystemSetting(key="maintenance_mode", value={"enabled": enabled})
        db.session.add(setting)

    db.session.commit()

    return jsonify({
        "message": "Maintenance mode updated",
        "enabled": enabled
    }), 200


# ---------------------------------------------------------
# ⭐ Ping
# ---------------------------------------------------------
@system_bp.route("/ping", methods=["GET"])
def system_ping():
    return jsonify({"message": "system ok"}), 200
