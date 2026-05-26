from flask import Blueprint, jsonify, request, Response, session
from database import db
from models.user import User
from models.billing import BillingEvent
from datetime import datetime, timedelta
import csv
from io import StringIO

admin_billing_bp = Blueprint("admin_billing", __name__)


# -----------------------------
# ADMIN AUTH CHECK
# -----------------------------
def require_admin():
    user_id = session.get("user_id")
    if not user_id:
        return None, jsonify({"error": "Not authenticated"}), 401

    user = User.query.get(user_id)
    if not user or user.role != "admin":
        return None, jsonify({"error": "Admin access required"}), 403

    return user, None, None


# -----------------------------
# BILLING HISTORY (JSON)
# -----------------------------
@admin_billing_bp.route("/billing/history", methods=["GET"])
def billing_history():
    _, err, code = require_admin()
    if err:
        return err, code

    user_id = request.args.get("user_id", type=int)
    feature = request.args.get("feature")
    category = request.args.get("category")
    start = request.args.get("start")
    end = request.args.get("end")

    q = BillingEvent.query

    if user_id:
        q = q.filter_by(user_id=user_id)
    if feature:
        q = q.filter_by(feature=feature)
    if category:
        q = q.filter_by(category=category)
    if start:
        q = q.filter(BillingEvent.created_at >= datetime.fromisoformat(start))
    if end:
        q = q.filter(BillingEvent.created_at <= datetime.fromisoformat(end))

    q = q.order_by(BillingEvent.created_at.desc())

    events = [e.as_dict() for e in q.limit(1000).all()]
    return jsonify({"events": events})


# -----------------------------
# BILLING EXPORT (CSV DOWNLOAD)
# -----------------------------
@admin_billing_bp.route("/billing/export", methods=["GET"])
def billing_export():
    _, err, code = require_admin()
    if err:
        return err, code

    q = BillingEvent.query.order_by(BillingEvent.created_at.desc())

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "id",
        "user_id",
        "plan",
        "category",
        "feature",
        "credits_used",
        "details",
        "created_at"
    ])

    for e in q.all():
        writer.writerow([
            e.id,
            e.user_id,
            e.plan,
            e.category,
            e.feature,
            e.credits_used,
            str(e.details or {}),
            e.created_at.isoformat(),
        ])

    output.seek(0)

    return Response(
        output.read(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=billing_export.csv"},
    )


# -----------------------------
# CREDIT USAGE BY MODEL / TOOL
# -----------------------------
@admin_billing_bp.route("/credits/by-model", methods=["GET"])
def credits_by_model():
    _, err, code = require_admin()
    if err:
        return err, code

    # Optional: last N days filter (default 7)
    days = request.args.get("days", default=7, type=int)
    since = datetime.utcnow() - timedelta(days=days)

    q = BillingEvent.query.filter(
        BillingEvent.credits_used > 0,
        BillingEvent.created_at >= since,
    )

    by_model = {}
    by_tool = {}

    for e in q.all():
        details = e.details or {}
        model = details.get("model")
        tool = details.get("tool")
        used = e.credits_used or 0

        if model:
            by_model[model] = by_model.get(model, 0) + used
        if tool:
            by_tool[tool] = by_tool.get(tool, 0) + used

    models = [
        {"name": name, "credits": credits}
        for name, credits in by_model.items()
    ]
    tools = [
        {"name": name, "credits": credits}
        for name, credits in by_tool.items()
    ]

    return jsonify({"models": models, "tools": tools})


# -----------------------------
# REVENUE / USAGE ANALYTICS
# -----------------------------
@admin_billing_bp.route("/revenue/analytics", methods=["GET"])
def revenue_analytics():
    _, err, code = require_admin()
    if err:
        return err, code

    # Default: last 7 days
    days = request.args.get("days", default=7, type=int)
    since = datetime.utcnow() - timedelta(days=days)

    q = BillingEvent.query.filter(
        BillingEvent.created_at >= since
    ).order_by(BillingEvent.created_at.asc())

    by_day = {}
    total_credits_used = 0

    for e in q.all():
        day = e.created_at.date().isoformat()
        used = e.credits_used or 0

        if day not in by_day:
            by_day[day] = {
                "credits_used": 0,
            }

        by_day[day]["credits_used"] += used
        total_credits_used += used

    daily = [
        {
            "date": day,
            "credits_used": data["credits_used"],
        }
        for day, data in sorted(by_day.items())
    ]

    # Later you can map credits -> real revenue using Stripe prices
    # e.g. revenue = credits_used * price_per_credit

    return jsonify({
        "daily": daily,
        "total_credits_used": total_credits_used,
    })
