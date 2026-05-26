from flask import Blueprint, jsonify, request
from utils.security_logger import log_security_event
from utils.alert_dispatcher import send_admin_alert
from utils.api_key_manager import generate_api_key, revoke_api_key
from models.api_key import ApiKey

api_keys_bp = Blueprint("api_keys_bp", __name__)

# ---------------------------------------------------------
# ⭐ LIST API KEYS
# ---------------------------------------------------------
@api_keys_bp.route("/list", methods=["GET"])
def list_keys():
    keys = ApiKey.query.order_by(ApiKey.created_at.desc()).all()

    return jsonify({
        "keys": [
            {
                "id": k.id,
                "label": k.label,
                "revoked": k.revoked,
                "created_at": k.created_at.isoformat(),
                "last_used": k.last_used.isoformat() if k.last_used else None,
                "usage_count": k.usage_count
            }
            for k in keys
        ]
    }), 200


# ---------------------------------------------------------
# ⭐ GENERATE NEW KEY
# ---------------------------------------------------------
@api_keys_bp.route("/generate", methods=["POST"])
def generate_key():
    data = request.get_json() or {}
    label = data.get("label", "Unnamed Key")

    raw_key = generate_api_key(label)

    log_security_event(f"Generated new API key: {label}")
    send_admin_alert("api", f"New API key created: {label}")

    return jsonify({
        "message": "API key generated",
        "key": raw_key
    }), 200


# ---------------------------------------------------------
# ⭐ REVOKE KEY
# ---------------------------------------------------------
@api_keys_bp.route("/revoke/<int:key_id>", methods=["POST"])
def revoke_key(key_id):
    ok = revoke_api_key(key_id)

    if not ok:
        return jsonify({"error": "Key not found"}), 404

    log_security_event(f"Revoked API key ID {key_id}")
    send_admin_alert("api", f"API key revoked (ID {key_id})")

    return jsonify({"message": "API key revoked"}), 200
