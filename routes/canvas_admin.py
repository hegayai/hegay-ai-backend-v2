from flask import Blueprint, jsonify, request
import os
import json

canvas_admin_bp = Blueprint("canvas_admin_bp", __name__)

ADMIN_DATA = "admin_data"
os.makedirs(ADMIN_DATA, exist_ok=True)

SETTINGS_FILE = os.path.join(ADMIN_DATA, "canvas_settings.json")

DEFAULT_SETTINGS = {
    "allowUploads": True,
    "maxUploadSizeMB": 25,
    "enableAI": True,
    "enableCustomFonts": True,
    "enableCustomShapes": True,
    "maintenanceMode": False
}


def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return DEFAULT_SETTINGS
    with open(SETTINGS_FILE, "r") as f:
        return json.load(f)


def save_settings(data):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=2)


@canvas_admin_bp.route("/admin/settings", methods=["GET"])
def get_settings():
    return jsonify({
        "status": "success",
        "settings": load_settings()
    })


@canvas_admin_bp.route("/admin/settings/update", methods=["POST"])
def update_settings():
    updates = request.json or {}
    settings = load_settings()

    for key, value in updates.items():
        if key in settings:
            settings[key] = value

    save_settings(settings)

    return jsonify({
        "status": "success",
        "message": "Settings updated",
        "settings": settings
    })


@canvas_admin_bp.route("/admin/stats", methods=["GET"])
def get_stats():
    stats = {
        "projects": len(os.listdir("projects")) if os.path.exists("projects") else 0,
        "assets": len(os.listdir("uploads/canvas_assets")) if os.path.exists("uploads/canvas_assets") else 0,
        "fonts": len(os.listdir("fonts")) if os.path.exists("fonts") else 0,
        "shapes": len(os.listdir("shapes")) if os.path.exists("shapes") else 0,
        "colorPalettes": len(os.listdir("color_palettes")) if os.path.exists("color_palettes") else 0,
        "usersWithPreferences": len(os.listdir("preferences")) if os.path.exists("preferences") else 0
    }

    return jsonify({
        "status": "success",
        "stats": stats
    })


@canvas_admin_bp.route("/admin/toggle-maintenance", methods=["POST"])
def toggle_maintenance():
    settings = load_settings()
    settings["maintenanceMode"] = not settings["maintenanceMode"]
    save_settings(settings)

    return jsonify({
        "status": "success",
        "maintenanceMode": settings["maintenanceMode"]
    })
