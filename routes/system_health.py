import os
import time
import psutil
from datetime import datetime
from flask import Blueprint, Response, jsonify

system_health_bp = Blueprint("system_health_bp", __name__)

START_TIME = time.time()

def get_health_snapshot():
    return {
        "cpu": psutil.cpu_percent(interval=None),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage("/").percent,
        "uptime": int(time.time() - START_TIME),
        "load": os.getloadavg()[0] if hasattr(os, "getloadavg") else 0,
        "timestamp": datetime.utcnow().isoformat()
    }

def stream_health():
    while True:
        snapshot = get_health_snapshot()
        yield f"data: {snapshot}\n\n"
        time.sleep(1)

@system_health_bp.route("/admin/health/stream")
def health_stream():
    return Response(stream_health(), mimetype="text/event-stream")

@system_health_bp.route("/admin/health")
def health_snapshot():
    return jsonify({
        "status": "success",
        "health": get_health_snapshot()
    })
