from flask import Blueprint, jsonify, request
from database import db
from models import SecurityEvent, User
from datetime import datetime

security_bp = Blueprint("security_bp", __name__)

# ---------------------------------------------------------
# LIST RECENT SECURITY EVENTS
# ---------------------------------------------------------
@security_bp.route("/events", methods=["GET"])
def list_security_events():
    try:
        events = (
            SecurityEvent.query
            .order_by(SecurityEvent.timestamp.desc())
            .limit(100)
            .all()
        )

        data = []
        for e in events:
            data.append({
                "id": e.id,
                "event_type": e.event_type,
                "description": e.description,
                "ip_address": e.ip_address,
                "timestamp": e.timestamp.isoformat(),
                "user": e.user.email if e.user else None
            })

        return jsonify({"events": data})

    except Exception as e:
        print("Security events error:", e)
        return jsonify({"error": "Failed to load security events"}), 500


# ---------------------------------------------------------
# LOG A SECURITY EVENT (used by middleware or admin tools)
# ---------------------------------------------------------
@security_bp.route("/log", methods=["POST"])
def log_security_event():
    try:
        data = request.json

        event_type = data.get("event_type")
        description = data.get("description")
        user_id = data.get("user_id")
        ip_address = request.remote_addr

        if not event_type or not description:
            return jsonify({"error": "event_type and description are required"}), 400

        event = SecurityEvent(
            event_type=event_type,
            description=description,
            user_id=user_id,
            ip_address=ip_address,
            timestamp=datetime.utcnow()
        )

        db.session.add(event)
        db.session.commit()

        return jsonify({"message": "Security event logged"})

    except Exception as e:
        print("Log security event error:", e)
        return jsonify({"error": "Failed to log event"}), 500


# ---------------------------------------------------------
# GET SECURITY EVENTS FOR A SPECIFIC USER
# ---------------------------------------------------------
@security_bp.route("/user/<int:user_id>", methods=["GET"])
def user_security_events(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        events = (
            SecurityEvent.query
            .filter_by(user_id=user_id)
            .order_by(SecurityEvent.timestamp.desc())
            .all()
        )

        data = []
        for e in events:
            data.append({
                "id": e.id,
                "event_type": e.event_type,
                "description": e.description,
                "ip_address": e.ip_address,
                "timestamp": e.timestamp.isoformat()
            })

        return jsonify({
            "user": user.email,
            "events": data
        })

    except Exception as e:
        print("User security events error:", e)
        return jsonify({"error": "Failed to load user events"}), 500
