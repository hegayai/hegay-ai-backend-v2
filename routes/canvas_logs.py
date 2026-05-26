import time
import os
from flask import Blueprint, Response, jsonify

canvas_logs_bp = Blueprint("canvas_logs_bp", __name__)

LOG_FILE = "system.log"
os.makedirs(".", exist_ok=True)

def stream_logs():
    last_size = 0
    while True:
        try:
            if os.path.exists(LOG_FILE):
                size = os.path.getsize(LOG_FILE)
                if size > last_size:
                    with open(LOG_FILE, "r") as f:
                        f.seek(last_size)
                        new_data = f.read()
                        last_size = size
                        for line in new_data.splitlines():
                            yield f"data: {line}\n\n"
            time.sleep(0.5)
        except Exception as e:
            yield f"data: ERROR: {str(e)}\n\n"
            time.sleep(1)

@canvas_logs_bp.route("/admin/logs/stream")
def logs_stream():
    return Response(stream_logs(), mimetype="text/event-stream")

@canvas_logs_bp.route("/admin/logs/clear", methods=["POST"])
def clear_logs():
    open(LOG_FILE, "w").close()
    return jsonify({"status": "success", "message": "Logs cleared"})
