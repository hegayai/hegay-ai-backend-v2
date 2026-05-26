from flask import Blueprint, request, jsonify
from utils.auto_publish_engine import publish_promo, get_promo

publish_bp = Blueprint("publish_bp", __name__)

# ADMIN: publish promo to a slot
@publish_bp.route("/admin/promo/publish", methods=["POST"])
def admin_publish_promo():
    data = request.get_json() or {}

    location = data.get("location")          # landing | dashboard | studio
    title = data.get("title", "")
    subtitle = data.get("subtitle", "")
    asset_url = data.get("asset_url", "")
    asset_type = data.get("asset_type", "image")
    language = data.get("language", "English")

    if not location or not asset_url:
        return jsonify({"error": "location and asset_url are required"}), 400

    slot = publish_promo(location, title, subtitle, asset_url, asset_type, language)

    return jsonify({
        "location": slot.location,
        "title": slot.title,
        "subtitle": slot.subtitle,
        "asset_url": slot.asset_url,
        "asset_type": slot.asset_type,
        "language": slot.language,
        "updated_at": slot.updated_at.isoformat()
    }), 200


# PUBLIC: get promo for a slot (landing/dashboard/studio)
@publish_bp.route("/promo/<location>", methods=["GET"])
def get_promo_slot(location):
    slot = get_promo(location)
    if not slot:
        return jsonify({"promo": None}), 200

    return jsonify({
        "location": slot.location,
        "title": slot.title,
        "subtitle": slot.subtitle,
        "asset_url": slot.asset_url,
        "asset_type": slot.asset_type,
        "language": slot.language,
        "updated_at": slot.updated_at.isoformat()
    }), 200
