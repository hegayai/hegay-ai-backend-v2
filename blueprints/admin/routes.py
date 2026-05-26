from flask import Blueprint, jsonify, request, session, Response, stream_with_context
from datetime import datetime, timedelta
from time import sleep
from database import db
from models.user import User
from models.admin_alert import AdminAlert

# Logging + Alerts
from utils.security_logger import log_security_event
from utils.alert_dispatcher import send_admin_alert

admin_bp = Blueprint("admin_bp", __name__)

# ---------------------------------------------------------
# ⭐ SIMPLE ADMIN GUARD (NO ROLES TABLE)
# ---------------------------------------------------------
@admin_bp.before_request
def admin_protect():
    if session.get("role") != "admin":
        return jsonify({"error": "Forbidden"}), 403


# ---------------------------------------------------------
# ⭐ DASHBOARD: OVERVIEW METRICS
# ---------------------------------------------------------
@admin_bp.route("/dashboard/metrics", methods=["GET"])
def dashboard_metrics():
    total_users = User.query.count()
    total_admins = User.query.filter_by(role="admin").count()

    last_7_days = datetime.utcnow() - timedelta(days=7)
    new_users = User.query.filter(User.created_at >= last_7_days).count()

    return jsonify({
        "total_users": total_users,
        "total_admins": total_admins,
        "new_users_7d": new_users,
    }), 200


# ---------------------------------------------------------
# ⭐ DASHBOARD: USER GROWTH (LAST 30 DAYS)
# ---------------------------------------------------------
@admin_bp.route("/dashboard/growth", methods=["GET"])
def dashboard_growth():
    today = datetime.utcnow().date()
    start_date = today - timedelta(days=30)

    growth_data = []

    for i in range(31):
        day = start_date + timedelta(days=i)
        count = User.query.filter(
            db.func.date(User.created_at) == day
        ).count()

        growth_data.append({
            "date": str(day),
            "signups": count
        })

    return jsonify({"growth": growth_data}), 200


# ---------------------------------------------------------
# ⭐ DASHBOARD: ROLE DISTRIBUTION (SIMPLE)
# ---------------------------------------------------------
@admin_bp.route("/dashboard/roles", methods=["GET"])
def dashboard_roles():
    admin_count = User.query.filter_by(role="admin").count()
    user_count = User.query.filter_by(role="user").count()

    return jsonify({
        "roles": [
            {"role": "admin", "count": admin_count},
            {"role": "user", "count": user_count},
        ]
    }), 200


# ---------------------------------------------------------
# ⭐ DASHBOARD: RECENT ACTIVITY
# ---------------------------------------------------------
@admin_bp.route("/dashboard/activity", methods=["GET"])
def dashboard_activity():
    users = (
        User.query.order_by(User.created_at.desc())
        .limit(20)
        .all()
    )

    activity = []
    for u in users:
        activity.append({
            "id": u.id,
            "email": u.email,
            "created_at": u.created_at.isoformat(),
            "role": u.role
        })

    return jsonify({"activity": activity}), 200


# ---------------------------------------------------------
# ⭐ SYSTEM MODE
# ---------------------------------------------------------
@admin_bp.route("/system/mode", methods=["GET", "POST"])
def system_mode():
    if request.method == "GET":
        return jsonify({"mode": "live"}), 200

    data = request.get_json()
    mode = data.get("mode", "live")

    log_security_event(f"Changed system mode to {mode}")
    send_admin_alert("system", f"System mode changed to {mode}")

    return jsonify({"message": "Mode updated", "mode": mode}), 200


# ---------------------------------------------------------
# ⭐ ENGINE CONTROLS
# ---------------------------------------------------------
@admin_bp.route("/system/engine", methods=["POST"])
def system_engine():
    action = request.get_json().get("action")

    log_security_event(f"Engine action executed: {action}")
    send_admin_alert("engine", f"Engine action executed: {action}")

    return jsonify({"message": f"Engine {action} executed"}), 200


# ---------------------------------------------------------
# ⭐ SECURITY CONTROLS
# ---------------------------------------------------------
@admin_bp.route("/system/security", methods=["POST"])
def system_security():
    action = request.get_json().get("action")

    log_security_event(f"Security action executed: {action}")
    send_admin_alert("security", f"Security action executed: {action}")

    return jsonify({"message": f"Security action {action} completed"}), 200


# ---------------------------------------------------------
# ⭐ LOGS VIEWER (STATIC)
# ---------------------------------------------------------
@admin_bp.route("/system/logs", methods=["GET"])
def system_logs():
    logs = [
        "System started",
        "Admin logged in",
        "Engine restarted",
        "Security key rotated"
    ]
    return jsonify({"logs": logs}), 200


# ---------------------------------------------------------
# ⭐ API KEY MANAGEMENT
# ---------------------------------------------------------
@admin_bp.route("/system/api-keys", methods=["GET", "POST"])
def api_keys():
    if request.method == "GET":
        return jsonify({"keys": ["key_12345", "key_67890"]}), 200

    log_security_event("Generated new API key")
    send_admin_alert("api", "New API key generated")

    return jsonify({"message": "New API key generated", "key": "key_new_abcdef"}), 200


# ---------------------------------------------------------
# ⭐ SYSTEM HEALTH ACTIONS
# ---------------------------------------------------------
@admin_bp.route("/system/actions", methods=["POST"])
def system_actions():
    action = request.get_json().get("action")

    log_security_event(f"System action executed: {action}")
    send_admin_alert("system", f"System action executed: {action}")

    return jsonify({"message": f"Action {action} executed"}), 200


# ---------------------------------------------------------
# ⭐ UPDATE USER ROLE (SIMPLE)
# ---------------------------------------------------------
@admin_bp.route("/users/<int:user_id>/role", methods=["POST"])
def admin_update_user_role(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json() or {}
    new_role = data.get("role", "user")

    user.role = new_role
    db.session.commit()

    log_security_event(f"Updated role for user {user.email}")
    send_admin_alert("roles", f"Role updated for user {user.email}")

    return jsonify({
        "message": "Role updated",
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role,
        }
    }), 200


# ---------------------------------------------------------
# ⭐ SECURITY LOGS ENDPOINT
# ---------------------------------------------------------
@admin_bp.route("/security/logs", methods=["GET"])
def security_logs():
    from models.security_log import SecurityLog

    logs = SecurityLog.query.order_by(SecurityLog.created_at.desc()).limit(100).all()

    return jsonify({
        "logs": [
            {
                "id": log.id,
                "event": log.event,
                "actor": log.actor,
                "ip": log.ip,
                "user_agent": log.user_agent,
                "created_at": log.created_at.isoformat()
            }
            for log in logs
        ]
    }), 200


# ---------------------------------------------------------
# ⭐ ALERTS STREAM (SSE)
# ---------------------------------------------------------
@admin_bp.route("/alerts/stream", methods=["GET"])
def alerts_stream():
    @stream_with_context
    def event_stream():
        last_id = request.args.get("last_id", type=int) or 0

        while True:
            new_alerts = (
                AdminAlert.query
                .filter(AdminAlert.id > last_id)
                .order_by(AdminAlert.id.asc())
                .all()
            )

            for alert in new_alerts:
                last_id = alert.id
                data = {
                    "id": alert.id,
                    "type": alert.type,
                    "message": alert.message,
                    "created_at": alert.created_at.isoformat(),
                    "read": alert.read,
                }
                yield f"data: {data}\n\n"

            sleep(2)

    return Response(event_stream(), mimetype="text/event-stream")
