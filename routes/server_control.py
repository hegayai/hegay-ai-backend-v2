import os
import shutil
from flask import Blueprint, jsonify, request

server_control_bp = Blueprint("server_control_bp", __name__)

CACHE_FOLDER = "cache"
TEMP_FOLDER = "temp"
RESTART_FLAG = "restart.flag"

os.makedirs(CACHE_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)

@server_control_bp.route("/admin/server/restart", methods=["POST"])
def restart_server():
    with open(RESTART_FLAG, "w") as f:
        f.write("restart")
    return jsonify({"status": "success", "message": "Server restart triggered"})

@server_control_bp.route("/admin/server/clear-cache", methods=["POST"])
def clear_cache():
    shutil.rmtree(CACHE_FOLDER, ignore_errors=True)
    os.makedirs(CACHE_FOLDER, exist_ok=True)
    return jsonify({"status": "success", "message": "Cache cleared"})

@server_control_bp.route("/admin/server/clear-temp", methods=["POST"])
def clear_temp():
    shutil.rmtree(TEMP_FOLDER, ignore_errors=True)
    os.makedirs(TEMP_FOLDER, exist_ok=True)
    return jsonify({"status": "success", "message": "Temp files cleared"})

@server_control_bp.route("/admin/server/rebuild-indexes", methods=["POST"])
def rebuild_indexes():
    # Placeholder for search/db index rebuild
    return jsonify({"status": "success", "message": "Indexes rebuilt"})

@server_control_bp.route("/admin/server/actions", methods=["GET"])
def list_actions():
    return jsonify({
        "status": "success",
        "actions": [
            "restart",
            "clear-cache",
            "clear-temp",
            "rebuild-indexes"
        ]
    })
