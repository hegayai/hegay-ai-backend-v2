from flask import Blueprint, jsonify

# FIX: Blueprint name must match what main.py imports
canvas_templates = Blueprint("canvas_templates", __name__)

@canvas_templates.route("/templates", methods=["GET"])
def get_templates():
    return jsonify({
        "templates": [
            {
                "id": "poster-1",
                "title": "Bold Poster",
                "category": "Posters",
                "thumbnail": "https://via.placeholder.com/400x300?text=Poster+1"
            },
            {
                "id": "quote-1",
                "title": "Minimal Quote",
                "category": "Quotes",
                "thumbnail": "https://via.placeholder.com/400x300?text=Quote+1"
            },
            {
                "id": "social-1",
                "title": "Instagram Promo",
                "category": "Social",
                "thumbnail": "https://via.placeholder.com/400x300?text=Social+1"
            }
        ]
    })
