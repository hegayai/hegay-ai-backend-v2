import os
from flask import Blueprint, jsonify, request, send_file
from werkzeug.utils import secure_filename

canvas_fonts_bp = Blueprint("canvas_fonts_bp", __name__)

FONTS_FOLDER = "fonts"
os.makedirs(FONTS_FOLDER, exist_ok=True)


@canvas_fonts_bp.route("/fonts", methods=["GET"])
def list_fonts():
    files = os.listdir(FONTS_FOLDER)
    fonts = [
        {
            "name": f.replace(".ttf", "").replace(".otf", ""),
            "filename": f,
            "url": f"http://127.0.0.1:5050/canvas/fonts/{f}"
        }
        for f in files if f.lower().endswith((".ttf", ".otf"))
    ]

    return jsonify({
        "status": "success",
        "fonts": fonts
    })


@canvas_fonts_bp.route("/fonts/upload", methods=["POST"])
def upload_font():
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "No font uploaded"}), 400

    file = request.files["file"]
    filename = secure_filename(file.filename)

    if not filename.lower().endswith((".ttf", ".otf")):
        return jsonify({"status": "error", "message": "Invalid font format"}), 400

    save_path = os.path.join(FONTS_FOLDER, filename)
    file.save(save_path)

    return jsonify({
        "status": "success",
        "filename": filename,
        "url": f"http://127.0.0.1:5050/canvas/fonts/{filename}"
    })


@canvas_fonts_bp.route("/fonts/<filename>", methods=["GET"])
def serve_font(filename):
    file_path = os.path.join(FONTS_FOLDER, filename)

    if not os.path.exists(file_path):
        return jsonify({"status": "error", "message": "Font not found"}), 404

    return send_file(file_path, mimetype="font/ttf")
