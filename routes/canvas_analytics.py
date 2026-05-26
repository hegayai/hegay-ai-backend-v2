import os
import json
from flask import Blueprint, jsonify

canvas_analytics_bp = Blueprint("canvas_analytics_bp", __name__)

def count_files(folder):
    if not os.path.exists(folder):
        return 0
    return len(os.listdir(folder))

@canvas_analytics_bp.route("/admin/analytics", methods=["GET"])
def analytics():
    data = {
        "projects": count_files("projects"),
        "assets": count_files("uploads/canvas_assets"),
        "fonts": count_files("fonts"),
        "shapes": count_files("shapes"),
        "palettes": count_files("color_palettes"),
        "usersWithPreferences": count_files("preferences"),

        # Placeholder AI usage (can be replaced with real logs)
        "aiUsage": {
            "backgrounds": 12,
            "objectRemovals": 7,
            "autoLayouts": 5
        },

        # Placeholder daily activity
        "dailyActivity": [
            {"day": "Mon", "value": 12},
            {"day": "Tue", "value": 18},
            {"day": "Wed", "value": 9},
            {"day": "Thu", "value": 22},
            {"day": "Fri", "value": 15},
            {"day": "Sat", "value": 7},
            {"day": "Sun", "value": 4},
        ]
    }

    return jsonify({"status": "success", "analytics": data})
