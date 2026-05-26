from flask import Blueprint, request, jsonify, session
from datetime import datetime
from database import db

security_bp = Blueprint("security", __name__)

# ---------------------------------------------------------
# ⭐ Security Event Model (inline for now)
# ---------------------------------------------------------
class SecurityEvent(db.Model):
    __tablename__ = "security_events"

    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    ip = db.Column(db.String(100))
    user_agent = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "event_type": self.event_type,
            "message": self.message,
            "ip": self.ip,
            "user_agent": self.user_agent,
            "created_at": self.created_at.isoformat(),
        }


# ---------------------------------------------------------
# ⭐ Helper: Log a security event
# ---------------------------------------------------------
def log_event(event_type, message):
    event = SecurityEvent(
        event_type=event_type,
        message=message,
        ip=request.remote_addr,
        user_agent=request.headers.get("User-Agent")
    )
    db.session.add(event)
    db.session.commit()


# ---------------------------------------------------------
# ⭐ Endpoint: List all security events (admin only)
# ---------------------------------------------------------
@security_bp.route("/events", methods=["GET"])
def list_events():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    if "admin" not in session.get("roles", []):
        return jsonify({"error": "Admin access required"}), 403

    events = SecurityEvent.query.order_by(SecurityEvent.id.desc()).all()
    return jsonify([e.to_dict() for e in events]), 200


# ---------------------------------------------------------
# ⭐ Endpoint: Log a manual security event
# ---------------------------------------------------------
@security_bp.route("/log", methods=["POST"])
def manual_log():
    data = request.get_json()
    event_type = data.get("event_type")
    message = data.get("message")

    if not event_type or not message:
        return jsonify({"error": "event_type and message required"}), 400

    log_event(event_type, message)

    return jsonify({"message": "Security event logged"}), 201


# ---------------------------------------------------------
# ⭐ Endpoint: Security heartbeat
# ---------------------------------------------------------
@security_bp.route("/ping", methods=["GET"])
def security_ping():
    log_event("ping", "Security heartbeat check")
    return jsonify({"message": "security ok"}), 200
