from flask import Blueprint, jsonify, session, request
from datetime import datetime
from database import db

analytics_bp = Blueprint("analytics", __name__)

# ---------------------------------------------------------
# ⭐ Analytics Event Model (fixed: metadata → data)
# ---------------------------------------------------------
class AnalyticsEvent(db.Model):
    __tablename__ = "analytics_events"

    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, nullable=True)
    data = db.Column(db.JSON, nullable=True)  # FIXED: renamed from metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "event_type": self.event_type,
            "user_id": self.user_id,
            "data": self.data,
            "created_at": self.created_at.isoformat(),
        }


# ---------------------------------------------------------
# ⭐ Helper: Admin check
# ---------------------------------------------------------
def require_admin():
    if "user_id" not in session:
        return False, {"error": "Not logged in"}, 401

    if "admin" not in session.get("roles", []):
        return False, {"error": "Admin access required"}, 403

    return True, None, None


# ---------------------------------------------------------
# ⭐ Track an analytics event
# ---------------------------------------------------------
@analytics_bp.route("/track", methods=["POST"])
def track_event():
    data = request.get_json()

    event_type = data.get("event_type")
    payload = data.get("metadata", {})  # still accept metadata from frontend

    if not event_type:
        return jsonify({"error": "event_type required"}), 400

    event = AnalyticsEvent(
        event_type=event_type,
        user_id=session.get("user_id"),
        data=payload  # FIXED: stored as data
    )

    db.session.add(event)
    db.session.commit()

    return jsonify({"message": "Event tracked"}), 201


# ---------------------------------------------------------
# ⭐ Admin: List all analytics events
# ---------------------------------------------------------
@analytics_bp.route("/events", methods=["GET"])
def list_events():
    ok, err, code = require_admin()
    if not ok:
        return jsonify(err), code

    events = AnalyticsEvent.query.order_by(AnalyticsEvent.id.desc()).all()
    return jsonify([e.to_dict() for e in events]), 200


# ---------------------------------------------------------
# ⭐ Admin: Summary metrics
# ---------------------------------------------------------
@analytics_bp.route("/summary", methods=["GET"])
def analytics_summary():
    ok, err, code = require_admin()
    if not ok:
        return jsonify(err), code

    total_events = AnalyticsEvent.query.count()
    login_events = AnalyticsEvent.query.filter_by(event_type="login").count()
    studio_events = AnalyticsEvent.query.filter_by(event_type="studio_action").count()

    return jsonify({
        "total_events": total_events,
        "login_events": login_events,
        "studio_events": studio_events
    }), 200


# ---------------------------------------------------------
# ⭐ Ping
# ---------------------------------------------------------
@analytics_bp.route("/ping", methods=["GET"])
def analytics_ping():
    return jsonify({"message": "analytics ok"}), 200
