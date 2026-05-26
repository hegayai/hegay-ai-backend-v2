from flask import Blueprint, request, jsonify
from utils.brand_style_memory import save_brand_style, get_brand_style, get_all_brand_styles

brand_style_bp = Blueprint("brand_style_bp", __name__)

@brand_style_bp.route("/save", methods=["POST"])
def save_style():
    data = request.get_json() or {}
    user_id = 1  # TODO: replace with real session user

    brand = save_brand_style(user_id, data)

    return jsonify({
        "status": "saved",
        "brand_name": brand.brand_name
    }), 200


@brand_style_bp.route("/get", methods=["POST"])
def get_style():
    data = request.get_json() or {}
    user_id = 1

    brand_name = data.get("brand_name")
    brand = get_brand_style(user_id, brand_name)

    if not brand:
        return jsonify({"error": "Brand not found"}), 404

    return jsonify({
        "brand_name": brand.brand_name,
        "logo_url": brand.logo_url,
        "primary_color": brand.primary_color,
        "secondary_color": brand.secondary_color,
        "accent_color": brand.accent_color,
        "font_family": brand.font_family,
        "font_weight": brand.font_weight,
        "font_style": brand.font_style,
        "design_language": brand.design_language,
        "tone": brand.tone
    }), 200


@brand_style_bp.route("/all", methods=["GET"])
def get_all_styles():
    user_id = 1
    brands = get_all_brand_styles(user_id)

    return jsonify([
        {
            "brand_name": b.brand_name,
            "logo_url": b.logo_url,
            "primary_color": b.primary_color,
            "secondary_color": b.secondary_color,
            "accent_color": b.accent_color,
            "font_family": b.font_family,
            "design_language": b.design_language,
            "tone": b.tone
        }
        for b in brands
    ]), 200
