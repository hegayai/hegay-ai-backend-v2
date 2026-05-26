import time
import json
import os
from flask import Blueprint, Response, request, jsonify

admin_notifications_bp = Blueprint("admin_notifications_bp", __name__)

NOTIF_FILE = "system_notifications.json"

if not os.path.exists(NOTIF_FILE):
    with open(NOTIF_FILE, "w") as f:
        json.dump([], f)

def load_notifications():
    with open(NOTIF_FILE, "r") as f:
        return json.load(f)

def save_notifications(data):
    with open(NOTIF_FILE, "w") as f:
        json.dump(data, f, indent=2)

# SSE stream
def stream_notifications():
    last_len = len(load_notifications())
    while True:
        notifs = load_notifications()
        if len(notifs) > last_len:
            new_items = notifs[last_len:]
            for item in new_items:
                yield f"data: {json.dumps(item)}\n\n"
            last_len = len(notifs)
        time.sleep(1)

@admin_notifications_bp.route("/admin/notifications/stream")
def notifications_stream():
    return Response(stream_notifications(), mimetype="text/event-stream")

@admin_notifications_bp.route("/admin/notifications/list")
def notifications_list():
    return jsonify({
        "status": "success",
        "notifications": load_notifications()
    })

@admin_notifications_bp.route("/admin/notifications/push", methods=["POST"])
def push_notification():
    data = request.json
    notif = {
        "id": str(int(time.time() * 1000)),
        "type": data.get("type", "info"),
        "title": data.get("title", "Untitled"),
        "message": data.get("message", ""),
        "timestamp": time.time()
    }

    all_notifs = load_notifications()
    all_notifs.append(notif)
    save_notifications(all_notifs)

    return jsonify({"status": "success", "notification": notif})
