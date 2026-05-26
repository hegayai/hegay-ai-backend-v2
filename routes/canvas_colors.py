import os
import json
from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

canvas_colors_bp = Blueprint("canvas_colors_bp", __name__)

COLOR_FOLDER = "color_palettes"
os.makedirs(COLOR_FOLDER, exist_ok=True)


@canvas_colors_bp.route("/colors", methods=["GET"])
def list_color_palettes():
    files = os.listdir(COLOR_FOLDER)
    palettes = []

    for f in files:
        if f.endswith(".json"):
            with open(os.path.join(COLOR_FOLDER, f), "r") as file:
                data = json.load(file)
                palettes.append(data)

    # Default palettes if none exist
    if not palettes:
        palettes = [
            {
                "id": "vibrant",
                "name": "Vibrant",
                "colors": ["#FF5733", "#FFC300", "#28A745", "#1E90FF", "#9B59B6"]
            },
            {
                "id": "pastel",
                "name": "Pastel",
                "colors": ["#FADADD", "#C7CEEA", "#B5EAD7", "#FFDAC1", "#E2F0CB"]
            },
            {
                "id": "darkmode",
                "name": "Dark Mode",
                "colors": ["#0A0A0A", "#1A1A1A", "#333333", "#555555", "#777777"]
            }
        ]

    return jsonify({
        "status": "success",
        "palettes": palettes
    })


@canvas_colors_bp.route("/colors/upload", methods=["POST"])
def upload_color_palette():
    palette_id = request.json.get("id")
    name = request.json.get("name")
    colors = request.json.get("colors", [])

    if not palette_id or not name or not colors:
        return jsonify({"status": "error", "message": "id, name, and colors required"}), 400

    filename = secure_filename(f"{palette_id}.json")
    save_path = os.path.join(COLOR_FOLDER, filename)

    with open(save_path, "w") as f:
        json.dump({
            "id": palette_id,
            "name": name,
            "colors": colors
        }, f, indent=2)

    return jsonify({
        "status": "success",
        "message": "Color palette saved",
        "palette_id": palette_id
    })


@canvas_colors_bp.route("/colors/<palette_id>", methods=["GET"])
def load_color_palette(palette_id):
    filename = secure_filename(f"{palette_id}.json")
    file_path = os.path.join(COLOR_FOLDER, filename)

    if not os.path.exists(file_path):
        return jsonify({"status": "error", "message": "Palette not found"}), 404

    with open(file_path, "r") as f:
        data = json.load(f)

    return jsonify({
        "status": "success",
        "palette": data
    })
