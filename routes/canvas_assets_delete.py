import os
from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

canvas_assets_delete_bp = Blueprint("canvas_assets_delete_bp", __name__)

ASSETS_FOLDER = "uploads/canvas_assets"

@canvas_assets_delete_bp.route("/assets/delete", methods=["POST"])
def delete_asset():
    filename = request.json.get("filename")

    if not filename:
        return jsonify({"status": "error", "message": "filename required"}), 400

    safe_name = secure_filename(filename)
    file_path = os.path.join(ASSETS_FOLDER, safe_name)

    if not os.path.exists(file_path):
        return jsonify({"status": "error", "message": "Asset not found"}), 404

    os.remove(file_path)

    return jsonify({
        "status": "success",
        "message": "Asset deleted",
        "filename": safe_name
    })
