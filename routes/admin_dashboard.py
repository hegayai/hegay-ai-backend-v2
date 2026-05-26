from flask import Blueprint, jsonify
from database import db
from models.user import User
from models.credit_transaction import CreditTransaction
from models.subscription import Subscription
from models.api_usage import ApiUsage
from sqlalchemy import func
from datetime import datetime, timedelta
import psutil

admin_dashboard = Blueprint("admin_dashboard", __name__)

# ---------------------------------------------------------
# METRICS (MAIN DASHBOARD CARDS + SYSTEM HEALTH)
# ---------------------------------------------------------
@admin_dashboard.route("/metrics", methods=["GET"])
def metrics():
    try:
        # Total users
        total_users = db.session.query(func.count(User.id)).scalar() or 0

        # Active users in last 30 days (using last_login)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_users = (
            db.session.query(func.count(User.id))
            .filter(User.last_login != None)
            .filter(User.last_login >= thirty_days_ago)
            .scalar()
            or 0
        )

        # API calls today
        api_calls_today = (
            db.session.query(func.count(ApiUsage.id))
            .filter(func.date(ApiUsage.timestamp) == datetime.utcnow().date())
            .scalar()
            or 0
        )

        # System health
        cpu_percent = psutil.cpu_percent(interval=0.2)
        memory_percent = psutil.virtual_memory().percent

        if cpu_percent < 40 and memory_percent < 60:
            system_load = "Normal"
        elif cpu_percent < 75 and memory_percent < 80:
            system_load = "Elevated"
        else:
            system_load = "High"

        return jsonify({
            "total_users": total_users,
            "active_users": active_users,
            "api_calls_today": api_calls_today,
            "system_load": system_load,
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent,
        })

    except Exception as e:
        print("Metrics error:", e)
        return jsonify({"error": "Failed to load metrics"}), 500


# ---------------------------------------------------------
# USER GROWTH (90 days)
# ---------------------------------------------------------
@admin_dashboard.route("/growth", methods=["GET"])
def growth():
    try:
        ninety_days_ago = datetime.utcnow() - timedelta(days=90)

        rows = (
            db.session.query(
                func.date(User.created_at).label("day"),
                func.count(User.id).label("total")
            )
            .filter(User.created_at >= ninety_days_ago)
            .group_by(func.date(User.created_at))
            .order_by(func.date(User.created_at))
            .all()
        )

        labels = [row.day.strftime("%Y-%m-%d") for row in rows]
        values = [int(row.total) for row in rows]

        return jsonify({"labels": labels, "values": values})

    except Exception as e:
        print("Growth error:", e)
        return jsonify({"error": "Failed to load growth"}), 500


# ---------------------------------------------------------
# API USAGE GRAPH (LAST 30 DAYS)
# ---------------------------------------------------------
@admin_dashboard.route("/api-usage-graph", methods=["GET"])
def api_usage_graph():
    try:
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        rows = (
            db.session.query(
                func.date(ApiUsage.timestamp).label("day"),
                func.count(ApiUsage.id).label("total")
            )
            .filter(ApiUsage.timestamp >= thirty_days_ago)
            .group_by(func.date(ApiUsage.timestamp))
            .order_by(func.date(ApiUsage.timestamp))
            .all()
        )

        labels = [row.day.strftime("%Y-%m-%d") for row in rows]
        values = [int(row.total) for row in rows]

        return jsonify({"labels": labels, "values": values})

    except Exception as e:
        print("API usage graph error:", e)
        return jsonify({"error": "Failed to load API usage graph"}), 500


# ---------------------------------------------------------
# RECENT ACTIVITY (from ApiUsage)
# ---------------------------------------------------------
@admin_dashboard.route("/activity", methods=["GET"])
def activity():
    try:
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        rows = (
            db.session.query(ApiUsage)
            .filter(ApiUsage.timestamp >= thirty_days_ago)
            .order_by(ApiUsage.timestamp.desc())
            .limit(100)
            .all()
        )

        events = []
        for r in rows:
            ts = r.timestamp.isoformat() if r.timestamp else None
            events.append({
                "id": r.id,
                "type": "api_call",
                "description": f"Endpoint {r.endpoint} used",
                "timestamp": ts,
                "user": r.user.email if r.user else None
            })

        return jsonify({"activities": events})

    except Exception as e:
        print("Activity error:", e)
        return jsonify({"error": "Failed to load activity"}), 500


# ---------------------------------------------------------
# REVENUE DASHBOARD
# ---------------------------------------------------------
@admin_dashboard.route("/revenue", methods=["GET"])
def revenue():
    try:
        total_revenue = db.session.query(func.sum(CreditTransaction.amount)).scalar() or 0
        credits_purchased = db.session.query(func.sum(CreditTransaction.credits)).scalar() or 0
        active_subscriptions = db.session.query(Subscription).filter_by(active=True).count()

        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        txs = (
            db.session.query(CreditTransaction)
            .filter(CreditTransaction.timestamp >= thirty_days_ago)
            .order_by(CreditTransaction.timestamp.desc())
            .limit(50)
            .all()
        )

        transactions = []
        for tx in txs:
            ts = tx.timestamp.isoformat() if tx.timestamp else None
            transactions.append({
                "id": tx.id,
                "user": tx.user.email if tx.user else "Unknown",
                "amount": float(tx.amount),
                "credits": tx.credits,
                "type": tx.type,
                "timestamp": ts
            })

        return jsonify({
            "total_revenue": float(total_revenue),
            "credits_purchased": int(credits_purchased),
            "active_subscriptions": active_subscriptions,
            "transactions": transactions
        })

    except Exception as e:
        print("Revenue error:", e)
        return jsonify({"error": "Failed to load revenue"}), 500
