from flask import Blueprint, jsonify

canvas_library_bp = Blueprint("canvas_library_bp", __name__)

@canvas_library_bp.route("/library", methods=["GET"])
def get_canvas_library():
    return jsonify({
        "items": [
            {
                "id": "canvas-1",
                "title": "Poster Design",
                "type": "Canvas",
                "thumbnail": "https://via.placeholder.com/400x300?text=Canvas+1"
            },
            {
                "id": "canvas-2",
                "title": "Brand Logo",
                "type": "Asset",
                "thumbnail": "https://via.placeholder.com/400x300?text=Logo"
            },
            {
                "id": "canvas-3",
                "title": "Social Template",
                "type": "Template",
                "thumbnail": "https://via.placeholder.com/400x300?text=Template"
            }
        ]
    })
