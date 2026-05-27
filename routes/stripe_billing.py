import os
from flask import Blueprint, jsonify, request, session
from database import db
from models.user import User
from models.credit_transaction import CreditTransaction
from models.billing import BillingEvent
from datetime import datetime
import stripe

# ---------------------------------------------------------
# BLUEPRINT
# ---------------------------------------------------------
stripe_billing_bp = Blueprint("stripe_billing_bp", __name__)

# ---------------------------------------------------------
# STRIPE CONFIG
# ---------------------------------------------------------
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# IMPORTANT: must match Render env var EXACTLY
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")


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
    db.session.commit()


# ---------------------------------------------------------
# CREATE CHECKOUT SESSION (CREDIT PACKS)
# ---------------------------------------------------------
@stripe_billing_bp.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    user, err, code = require_auth()
    if err:
        return err, code

    data = request.get_json() or {}
    price_id = data.get("price_id")
    credits = data.get("credits")

    if not price_id or not credits:
        return jsonify({"error": "price_id and credits are required"}), 400

    try:
        session_obj = stripe.checkout.Session.create(
            mode="payment",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=os.getenv("STRIPE_SUCCESS_URL"),
            cancel_url=os.getenv("STRIPE_CANCEL_URL"),
            metadata={
                "user_id": str(user.id),
                "credits": str(credits),
            },
        )
        return jsonify({"url": session_obj.url})

    except Exception as e:
        print("Stripe checkout error:", e)
        return jsonify({"error": "Failed to create checkout session"}), 500


# ---------------------------------------------------------
# STRIPE WEBHOOK (CREDIT PACKS)
# ---------------------------------------------------------
@stripe_billing_bp.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    # Verify signature
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, WEBHOOK_SECRET
        )
    except Exception as e:
        print("Stripe webhook signature error:", e)
        return jsonify({"error": "Invalid signature"}), 400

    # -----------------------------------------------------
    # CREDIT PACK PURCHASE
    # -----------------------------------------------------
    if event["type"] == "checkout.session.completed":
        session_obj = event["data"]["object"]
        metadata = session_obj.get("metadata") or {}

        user_id = metadata.get("user_id")
        credits_str = metadata.get("credits", "0")

        try:
            credits = int(credits_str)
        except ValueError:
            credits = 0

        if user_id and credits > 0:
            user = User.query.get(int(user_id))
            if user:

                # Add credits to user
                user.credits_total += credits

                # Log credit transaction
                tx = CreditTransaction(
                    user_id=user.id,
                    amount=credits,
                    type="CREDITS_PURCHASED",
                    meta_data={
                        "stripe_session_id": session_obj.get("id"),
                        "amount_total": session_obj.get("amount_total"),
                        "currency": session_obj.get("currency"),
                        "credits_added": credits,
                    },
                    created_at=datetime.utcnow(),
                )
                db.session.add(tx)

                # Log billing event
                log_billing_event(
                    user_id=user.id,
                    category="purchase",
                    feature="credit_pack",
                    credits_used=0,
                    plan=user.plan,
                    details={
                        "stripe_session_id": session_obj.get("id"),
                        "amount_total": session_obj.get("amount_total"),
                        "currency": session_obj.get("currency"),
                        "credits_added": credits,
                    },
                )

                db.session.commit()

    return "", 200
