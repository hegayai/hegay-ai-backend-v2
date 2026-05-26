import os
from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

canvas_fonts_delete_bp = Blueprint("canvas_fonts_delete_bp", __name__)

FONTS_FOLDER = "fonts"

@canvas_fonts_delete_bp.route("/fonts/delete", methods=["POST"])
def delete_font():
    filename = request.json.get("filename")

    if not filename:
        return jsonify({"status": "error", "message": "filename required"}), 400

    safe_name = secure_filename(filename)
    file_path = os.path.join(FONTS_FOLDER, safe_name)

    if not os.path.exists(file_path):
        return jsonify({"status": "error", "message": "Font not found"}), 404

    os.remove(file_path)

    return jsonify({
        "status": "success",
        "message": "Font deleted",
        "filename": safe_name
    })
