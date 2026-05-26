from flask import Blueprint, jsonify, session, request
from database import db
from models.user import User
from models.billing import BillingEvent
from datetime import datetime

credits_bp = Blueprint("credits_bp", __name__)


# ---------------------------------------------------------
# AUTH HELPER
# ---------------------------------------------------------
def require_auth():
    user_id = session.get("user_id")
    if not user_id:
        return None, jsonify({"error": "Unauthorized"}), 401

    user = User.query.get(user_id)
    if not user:
        return None, jsonify({"error": "Unauthorized"}), 401

    return user, None, None


# ---------------------------------------------------------
# BILLING EVENT LOGGER
# ---------------------------------------------------------
def log_billing_event(user_id, category, feature, credits_used, details=None, plan=None):
    event = BillingEvent(
        user_id=user_id,
        plan=plan,
        category=category,
        feature=feature,
        credits_used=credits_used,
        details=details or {},
        created_at=datetime.utcnow(),
    )
    db.session.add(event)


# ---------------------------------------------------------
# CREDIT ENGINE HELPERS
# ---------------------------------------------------------
def deduct_credits(user: User, amount: int, category: str, feature: str, details=None):
    if amount <= 0:
        return

    if user.credits_remaining < amount:
        raise ValueError("Insufficient credits")

    user.credits_used += amount

    log_billing_event(
        user_id=user.id,
        category=category,
        feature=feature,
        credits_used=amount,
        details=details,
        plan=user.plan,
    )

    db.session.commit()


def add_credits(user: User, amount: int, category: str, feature: str, details=None):
    if amount <= 0:
        return

    user.credits_total += amount

    log_billing_event(
        user_id=user.id,
        category=category,
        feature=feature,
        credits_used=0,
        details=details,
        plan=user.plan,
    )

    db.session.commit()


# ---------------------------------------------------------
# USER CREDIT BALANCE
# ---------------------------------------------------------
@credits_bp.route("/balance", methods=["GET"])
def credits_balance():
    user, err, code = require_auth()
    if err:
        return err, code

    return jsonify({
        "credits_total": user.credits_total,
        "credits_used": user.credits_used,
        "credits_remaining": user.credits_remaining,
        "plan": user.plan,
    })


# ---------------------------------------------------------
# USER CREDIT LOGS
# ---------------------------------------------------------
@credits_bp.route("/logs", methods=["GET"])
def credits_logs():
    user, err, code = require_auth()
    if err:
        return err, code

    limit = request.args.get("limit", default=100, type=int)

    q = (
        BillingEvent.query
        .filter_by(user_id=user.id)
        .order_by(BillingEvent.created_at.desc())
        .limit(limit)
    )

    events = []
    for e in q.all():
        if hasattr(e, "as_dict"):
            events.append(e.as_dict())
        else:
            events.append({
                "id": e.id,
                "category": e.category,
                "feature": e.feature,
                "credits_used": e.credits_used,
                "details": e.details,
                "plan": e.plan,
                "created_at": e.created_at.isoformat() if e.created_at else None
            })

    return jsonify({"events": events})
