from flask import Blueprint, jsonify

canvas_brand_kit_bp = Blueprint("canvas_brand_kit_bp", __name__)

@canvas_brand_kit_bp.route("/brand-kit", methods=["GET"])
def brand_kit():
    return jsonify({
        "colors": ["#FF5733", "#1E90FF", "#28A745", "#FFC300"],
        "fonts": ["Inter", "Poppins", "Montserrat"],
        "logos": [
            "https://via.placeholder.com/200x200?text=Logo+1",
            "https://via.placeholder.com/200x200?text=Logo+2"
        ]
    })
