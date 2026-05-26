import os
import json
from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

canvas_text_styles_bp = Blueprint("canvas_text_styles_bp", __name__)

TEXT_STYLES_FOLDER = "text_styles"
os.makedirs(TEXT_STYLES_FOLDER, exist_ok=True)


# Default built‑in text styles
DEFAULT_TEXT_STYLES = [
    {
        "id": "heading-1",
        "name": "Heading 1",
        "font": "Inter",
        "size": 48,
        "weight": 700,
        "color": "#FFFFFF",
        "lineHeight": 1.2
    },
    {
        "id": "heading-2",
        "name": "Heading 2",
        "font": "Inter",
        "size": 36,
        "weight": 600,
        "color": "#FFFFFF",
        "lineHeight": 1.25
    },
    {
        "id": "body",
        "name": "Body Text",
        "font": "Inter",
        "size": 20,
        "weight": 400,
        "color": "#CCCCCC",
        "lineHeight": 1.4
    }
]


@canvas_text_styles_bp.route("/text-styles", methods=["GET"])
def list_text_styles():
    styles = DEFAULT_TEXT_STYLES.copy()

    # Load custom styles
    for f in os.listdir(TEXT_STYLES_FOLDER):
        if f.endswith(".json"):
            with open(os.path.join(TEXT_STYLES_FOLDER, f), "r") as file:
                data = json.load(file)
                styles.append(data)

    return jsonify({
        "status": "success",
        "styles": styles
    })


@canvas_text_styles_bp.route("/text-styles/upload", methods=["POST"])
def upload_text_style():
    style_id = request.json.get("id")
    name = request.json.get("name")
    font = request.json.get("font")
    size = request.json.get("size")
    weight = request.json.get("weight")
    color = request.json.get("color")
    lineHeight = request.json.get("lineHeight", 1.2)

    if not style_id or not name or not font or not size:
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    filename = secure_filename(f"{style_id}.json")
    save_path = os.path.join(TEXT_STYLES_FOLDER, filename)

    with open(save_path, "w") as f:
        json.dump({
            "id": style_id,
            "name": name,
            "font": font,
            "size": size,
            "weight": weight,
            "color": color,
            "lineHeight": lineHeight
        }, f, indent=2)

    return jsonify({
        "status": "success",
        "message": "Text style saved",
        "style_id": style_id
    })


@canvas_text_styles_bp.route("/text-styles/<style_id>", methods=["GET"])
def load_text_style(style_id):
    filename = secure_filename(f"{style_id}.json")
    file_path = os.path.join(TEXT_STYLES_FOLDER, filename)

    # Check custom styles
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
        return jsonify({
            "status": "success",
            "style": data
        })

    # Check built‑in styles
    for style in DEFAULT_TEXT_STYLES:
        if style["id"] == style_id:
            return jsonify({
                "status": "success",
                "style": style
            })

    return jsonify({"status": "error", "message": "Text style not found"}), 404
