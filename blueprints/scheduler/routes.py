from flask import Blueprint, request, jsonify
from datetime import datetime
from utils.auto_scheduler import schedule_promo, run_due_schedules
from models.scheduled_promo import ScheduledPromo

scheduler_bp = Blueprint("scheduler_bp", __name__)

# ---------------------------------------------------------
# CREATE A SCHEDULED PROMO
# ---------------------------------------------------------
@scheduler_bp.route("/admin/promo/schedule", methods=["POST"])
def admin_schedule_promo():
    data = request.get_json() or {}

    required = ["location", "asset_url", "scheduled_for"]
    if any(k not in data for k in required):
        return jsonify({"error": "location, asset_url, scheduled_for required"}), 400

    try:
        scheduled_for = datetime.fromisoformat(data["scheduled_for"])
    except Exception:
        return jsonify({"error": "scheduled_for must be ISO datetime"}), 400

    promo = schedule_promo(
        location=data["location"],
        title=data.get("title", ""),
        subtitle=data.get("subtitle", ""),
        asset_url=data["asset_url"],
        asset_type=data.get("asset_type", "image"),
        language=data.get("language", "English"),
        scheduled_for=scheduled_for
    )

    return jsonify({
        "id": promo.id,
        "location": promo.location,
        "title": promo.title,
        "subtitle": promo.subtitle,
        "asset_url": promo.asset_url,
        "asset_type": promo.asset_type,
        "language": promo.language,
        "scheduled_for": promo.scheduled_for.isoformat(),
        "status": promo.status,
        "created_at": promo.created_at.isoformat(),
    }), 201


# ---------------------------------------------------------
# LIST ALL SCHEDULED PROMOS (FOR TIMELINE)
# ---------------------------------------------------------
@scheduler_bp.route("/admin/promo/scheduled", methods=["GET"])
def list_scheduled_promos():
    promos = ScheduledPromo.query.order_by(ScheduledPromo.scheduled_for.asc()).all()

    return jsonify({
        "promos": [
            {
                "id": p.id,
                "location": p.location,
                "title": p.title,
                "subtitle": p.subtitle,
                "asset_url": p.asset_url,
                "asset_type": p.asset_type,
                "language": p.language,
                "scheduled_for": p.scheduled_for.isoformat(),
                "status": p.status,
            }
            for p in promos
        ]
    }), 200


# ---------------------------------------------------------
# UPDATE SCHEDULED PROMO TIME (DRAG-AND-DROP)
# ---------------------------------------------------------
@scheduler_bp.route("/admin/promo/scheduled/<int:promo_id>", methods=["PATCH"])
def update_scheduled_promo(promo_id):
    data = request.get_json() or {}
    new_time_str = data.get("scheduled_for")

    if not new_time_str:
        return jsonify({"error": "scheduled_for is required"}), 400

    try:
        new_time = datetime.fromisoformat(new_time_str)
    except Exception:
        return jsonify({"error": "scheduled_for must be ISO datetime"}), 400

    promo = ScheduledPromo.query.get(promo_id)
    if not promo:
        return jsonify({"error": "Promo not found"}), 404

    promo.scheduled_for = new_time
    # If it was executed before and you're moving it, reset status if you want:
    if promo.status == "executed":
        promo.status = "pending"
        promo.executed_at = None

    from database import db
    db.session.commit()

    return jsonify({
        "id": promo.id,
        "scheduled_for": promo.scheduled_for.isoformat(),
        "status": promo.status,
    }), 200


# ---------------------------------------------------------
# RUN SCHEDULER (CRON OR MANUAL)
# ---------------------------------------------------------
@scheduler_bp.route("/admin/promo/run-scheduler", methods=["POST"])
def admin_run_scheduler():
    executed = run_due_schedules()

    return jsonify({
        "executed_count": len(executed),
        "executed_ids": [p.id for p in executed]
    }), 200
