from flask import Blueprint, request, jsonify
from datetime import datetime
from database import db
from models.recurring_promo import RecurringPromo
from utils.recurring_engine import run_recurring_promos

recurring_bp = Blueprint("recurring_bp", __name__)

# ---------------------------------------------------------
# CREATE RECURRING PROMO
# ---------------------------------------------------------
@recurring_bp.route("/admin/promo/recurring", methods=["POST"])
def create_recurring_promo():
    data = request.get_json() or {}

    required = ["location", "asset_url", "recurrence_type", "recurrence_value"]
    if any(k not in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400

    rp = RecurringPromo(
        location=data["location"],
        title=data.get("title", ""),
        subtitle=data.get("subtitle", ""),
        asset_url=data["asset_url"],
        asset_type=data.get("asset_type", "image"),
        language=data.get("language", "English"),
        recurrence_type=data["recurrence_type"],
        recurrence_value=data["recurrence_value"],
    )

    db.session.add(rp)
    db.session.commit()

    return jsonify({
        "id": rp.id,
        "location": rp.location,
        "recurrence_type": rp.recurrence_type,
        "recurrence_value": rp.recurrence_value
    }), 201


# ---------------------------------------------------------
# LIST RECURRING PROMOS
# ---------------------------------------------------------
@recurring_bp.route("/admin/promo/recurring", methods=["GET"])
def list_recurring_promos():
    promos = RecurringPromo.query.all()

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
                "recurrence_type": p.recurrence_type,
                "recurrence_value": p.recurrence_value,
                "last_executed": p.last_executed.isoformat() if p.last_executed else None,
            }
            for p in promos
        ]
    }), 200


# ---------------------------------------------------------
# RUN RECURRING ENGINE
# ---------------------------------------------------------
@recurring_bp.route("/admin/promo/run-recurring", methods=["POST"])
def run_recurring():
    executed = run_recurring_promos()

    return jsonify({
        "executed_count": len(executed),
        "executed_ids": [p.id for p in executed]
    }), 200
