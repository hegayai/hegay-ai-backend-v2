import os
from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

canvas_colors_delete_bp = Blueprint("canvas_colors_delete_bp", __name__)

PALETTES_FOLDER = "color_palettes"

@canvas_colors_delete_bp.route("/colors/delete", methods=["POST"])
def delete_palette():
    palette_id = request.json.get("palette_id")

    if not palette_id:
        return jsonify({"status": "error", "message": "palette_id required"}), 400

    filename = secure_filename(f"{palette_id}.json")
    file_path = os.path.join(PALETTES_FOLDER, filename)

    if not os.path.exists(file_path):
        return jsonify({"status": "error", "message": "Palette not found"}), 404

    os.remove(file_path)

    return jsonify({
        "status": "success",
        "message": "Palette deleted",
        "palette_id": palette_id
    })
