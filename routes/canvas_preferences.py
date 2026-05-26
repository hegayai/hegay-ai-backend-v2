import os
import json
from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

canvas_preferences_bp = Blueprint("canvas_preferences_bp", __name__)

PREFERENCES_FOLDER = "preferences"
os.makedirs(PREFERENCES_FOLDER, exist_ok=True)


@canvas_preferences_bp.route("/preferences/save", methods=["POST"])
def save_preferences():
    user_id = request.json.get("user_id", "default")
    prefs = request.json.get("preferences", {})

    filename = secure_filename(f"{user_id}.json")
    save_path = os.path.join(PREFERENCES_FOLDER, filename)

    with open(save_path, "w") as f:
        json.dump(prefs, f, indent=2)

    return jsonify({
        "status": "success",
        "message": "Preferences saved",
        "user_id": user_id
    })


@canvas_preferences_bp.route("/preferences/load/<user_id>", methods=["GET"])
def load_preferences(user_id):
    filename = secure_filename(f"{user_id}.json")
    file_path = os.path.join(PREFERENCES_FOLDER, filename)

    if not os.path.exists(file_path):
        return jsonify({
            "status": "success",
            "preferences": {
                "snapToGrid": True,
                "showRulers": True,
                "defaultFont": "Inter",
                "defaultColor": "#ffffff",
                "canvasBackground": "#0A0A0A"
            }
        })

    with open(file_path, "r") as f:
        data = json.load(f)

    return jsonify({
        "status": "success",
        "preferences": data
    })


@canvas_preferences_bp.route("/preferences/list", methods=["GET"])
def list_preferences():
    files = os.listdir(PREFERENCES_FOLDER)
    users = [f.replace(".json", "") for f in files if f.endswith(".json")]

    return jsonify({
        "status": "success",
        "users": users
    })
