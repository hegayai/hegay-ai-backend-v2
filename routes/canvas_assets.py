import os
from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

canvas_assets_bp = Blueprint("canvas_assets_bp", __name__)

UPLOAD_FOLDER = "uploads/canvas_assets"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@canvas_assets_bp.route("/assets", methods=["GET"])
def list_assets():
    files = os.listdir(UPLOAD_FOLDER)
    assets = [
        {
            "filename": f,
            "url": f"http://127.0.0.1:5050/canvas/assets/{f}"
        }
        for f in files
    ]

    return jsonify({
        "status": "success",
        "assets": assets
    })


@canvas_assets_bp.route("/assets/upload", methods=["POST"])
def upload_asset():
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "No file uploaded"}), 400

    file = request.files["file"]
    filename = secure_filename(file.filename)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)

    return jsonify({
        "status": "success",
        "filename": filename,
        "url": f"http://127.0.0.1:5050/canvas/assets/{filename}"
    })


@canvas_assets_bp.route("/assets/<filename>", methods=["GET"])
def serve_asset(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    if not os.path.exists(file_path):
        return jsonify({"status": "error", "message": "File not found"}), 404

    with open(file_path, "rb") as f:
        data = f.read()

    return data
