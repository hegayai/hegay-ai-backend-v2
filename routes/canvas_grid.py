import os
import json
from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

canvas_grid_bp = Blueprint("canvas_grid_bp", __name__)

GRID_FOLDER = "grid_settings"
os.makedirs(GRID_FOLDER, exist_ok=True)


def grid_file(user_id):
    filename = secure_filename(f"{user_id}_grid.json")
    return os.path.join(GRID_FOLDER, filename)


# Default grid + guide settings
DEFAULT_GRID_SETTINGS = {
    "snapToGrid": True,
    "gridSize": 20,
    "showGrid": True,
    "showRulers": True,
    "guides": [],
    "snapToGuides": True
}


@canvas_grid_bp.route("/grid/load/<user_id>", methods=["GET"])
def load_grid(user_id):
    file_path = grid_file(user_id)

    if not os.path.exists(file_path):
        return jsonify({
            "status": "success",
            "settings": DEFAULT_GRID_SETTINGS
        })

    with open(file_path, "r") as f:
        data = json.load(f)

    return jsonify({
        "status": "success",
        "settings": data
    })


@canvas_grid_bp.route("/grid/save", methods=["POST"])
def save_grid():
    user_id = request.json.get("user_id", "default")
    settings = request.json.get("settings", {})

    file_path = grid_file(user_id)

    with open(file_path, "w") as f:
        json.dump(settings, f, indent=2)

    return jsonify({
        "status": "success",
        "message": "Grid settings saved",
        "user_id": user_id
    })


@canvas_grid_bp.route("/grid/add-guide", methods=["POST"])
def add_guide():
    user_id = request.json.get("user_id", "default")
    position = request.json.get("position")
    orientation = request.json.get("orientation")  # "vertical" or "horizontal"

    if position is None or orientation not in ["vertical", "horizontal"]:
        return jsonify({"status": "error", "message": "Invalid guide"}), 400

    file_path = grid_file(user_id)

    # Load existing or default
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            settings = json.load(f)
    else:
        settings = DEFAULT_GRID_SETTINGS.copy()

    settings.setdefault("guides", [])
    settings["guides"].append({
        "position": position,
        "orientation": orientation
    })

    with open(file_path, "w") as f:
        json.dump(settings, f, indent=2)

    return jsonify({
        "status": "success",
        "message": "Guide added",
        "guides": settings["guides"]
    })


@canvas_grid_bp.route("/grid/clear-guides", methods=["POST"])
def clear_guides():
    user_id = request.json.get("user_id", "default")

    file_path = grid_file(user_id)

    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            settings = json.load(f)
    else:
        settings = DEFAULT_GRID_SETTINGS.copy()

    settings["guides"] = []

    with open(file_path, "w") as f:
        json.dump(settings, f, indent=2)

    return jsonify({
        "status": "success",
        "message": "Guides cleared"
    })
