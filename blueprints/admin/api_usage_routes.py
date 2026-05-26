from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from database import db
from models.api_key import ApiKey
from models.api_usage import ApiUsage

api_usage_bp = Blueprint("api_usage_bp", __name__)

# ---------------------------------------------------------
# ⭐ PER-KEY DAILY USAGE (LAST 7 DAYS)
# ---------------------------------------------------------
@api_usage_bp.route("/daily", methods=["GET"])
def daily_usage():
    days = 7
    end = datetime.utcnow().date()
    start = end - timedelta(days=days - 1)

    keys = ApiKey.query.all()
    result = []

    for key in keys:
        series = []
        for i in range(days):
            day = start + timedelta(days=i)
            count = (
                ApiUsage.query
                .filter(
                    ApiUsage.api_key_id == key.id,
                    db.func.date(ApiUsage.timestamp) == day
                )
                .count()
            )
            series.append({
                "date": str(day),
                "count": count
            })
        result.append({
            "key_id": key.id,
            "label": key.label,
            "data": series
        })

    return jsonify({"usage": result}), 200


# ---------------------------------------------------------
# ⭐ STATUS CODE DISTRIBUTION (LAST 24H)
# ---------------------------------------------------------
@api_usage_bp.route("/status", methods=["GET"])
def status_distribution():
    since = datetime.utcnow() - timedelta(hours=24)

    rows = (
        db.session.query(ApiUsage.status_code, db.func.count(ApiUsage.id))
        .filter(ApiUsage.timestamp >= since)
        .group_by(ApiUsage.status_code)
        .all()
    )

    data = [
        {"status": status, "count": count}
        for status, count in rows
    ]

    return jsonify({"status": data}), 200


# ---------------------------------------------------------
# ⭐ LATENCY STATS (LAST 24H)
# ---------------------------------------------------------
@api_usage_bp.route("/latency", methods=["GET"])
def latency_stats():
    since = datetime.utcnow() - timedelta(hours=24)

    rows = (
        db.session.query(
            db.func.avg(ApiUsage.latency_ms),
            db.func.max(ApiUsage.latency_ms),
            db.func.min(ApiUsage.latency_ms),
        )
        .filter(ApiUsage.timestamp >= since)
        .first()
    )

    avg_ms, max_ms, min_ms = rows if rows else (0, 0, 0)

    return jsonify({
        "latency": {
            "avg_ms": int(avg_ms or 0),
            "max_ms": int(max_ms or 0),
            "min_ms": int(min_ms or 0),
        }
    }), 200
