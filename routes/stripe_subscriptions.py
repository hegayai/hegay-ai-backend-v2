import os
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request, session
from database import db
from models.user import User
from models.subscription import Subscription
from models.billing import BillingEvent
from models.credit_transaction import CreditTransaction
from pricing.plans import PLANS
import stripe

stripe_subscriptions_bp = Blueprint("stripe_subscriptions_bp", __name__)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
SUBS_WEBHOOK_SECRET = os.getenv("STRIPE_SUBSCRIPTIONS_WEBHOOK_SECRET")

# Map internal plan names → Stripe price IDs (set these in env)
PLAN_PRICE_IDS = {
    "Starter": os.getenv("STRIPE_PRICE_STARTER"),
    "Creator": os.getenv("STRIPE_PRICE_CREATOR"),
    "Pro": os.getenv("STRIPE_PRICE_PRO"),
    "Studio": os.getenv("STRIPE_PRICE_STUDIO"),
}


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
# APPLY PLAN TO USER (CORE LOGIC)
# ---------------------------------------------------------
def apply_plan_to_user(user: User, plan_name: str, stripe_sub_id: str = None):
    """
    Syncs User + Subscription + credits with a given plan.
    """
    if plan_name not in PLANS:
        raise ValueError(f"Unknown plan: {plan_name}")

    plan_cfg = PLANS[plan_name]

    # Update user plan
    user.plan = plan_name

    # Monthly credits logic (simple: images count as credits)
    monthly_credits = plan_cfg.get("images", 0)

    # Reset usage and allocate new credits
    user.credits_total = monthly_credits
    user.credits_used = 0

    # Subscription record
    now = datetime.utcnow()
    end_date = now + timedelta(days=30)

    # Deactivate existing subscriptions
    Subscription.query.filter_by(user_id=user.id, active=True).update(
        {"active": False}
    )

    sub = Subscription(
        user_id=user.id,
        plan=plan_name,
        active=True,
        start_date=now,
        end_date=end_date,
        renewed_at=now,
    )
    db.session.add(sub)

    # Optional: log billing event for plan change
    log_billing_event(
        user_id=user.id,
        category="subscription",
        feature="plan_change",
        credits_used=0,
        plan=plan_name,
        details={
            "stripe_subscription_id": stripe_sub_id,
            "monthly_credits": monthly_credits,
        },
    )


# ---------------------------------------------------------
# CREATE SUBSCRIPTION CHECKOUT SESSION
# ---------------------------------------------------------
@stripe_subscriptions_bp.route("/create-subscription-session", methods=["POST"])
def create_subscription_session():
    user, err, code = require_auth()
    if err:
        return err, code

    data = request.get_json() or {}
    plan_name = data.get("plan")

    if plan_name not in PLAN_PRICE_IDS:
        return jsonify({"error": "Invalid plan"}), 400

    price_id = PLAN_PRICE_IDS[plan_name]
    if not price_id:
        return jsonify({"error": f"Stripe price not configured for {plan_name}"}), 500

    try:
        # Ensure Stripe customer
        if not user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=user.email,
                metadata={"user_id": str(user.id)},
            )
            user.stripe_customer_id = customer["id"]
            db.session.commit()

        session_obj = stripe.checkout.Session.create(
            mode="subscription",
            customer=user.stripe_customer_id,
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=os.getenv("STRIPE_SUB_SUCCESS_URL"),
            cancel_url=os.getenv("STRIPE_SUB_CANCEL_URL"),
            metadata={
                "user_id": str(user.id),
                "plan": plan_name,
            },
        )

        return jsonify({"url": session_obj.url})

    except Exception as e:
        print("Stripe subscription checkout error:", e)
        return jsonify({"error": "Failed to create subscription session"}), 500


# ---------------------------------------------------------
# CUSTOMER PORTAL
# ---------------------------------------------------------
@stripe_subscriptions_bp.route("/customer-portal", methods=["POST"])
def customer_portal():
    user, err, code = require_auth()
    if err:
        return err, code

    if not user.stripe_customer_id:
        return jsonify({"error": "No Stripe customer found"}), 400

    try:
        portal_session = stripe.billing_portal.Session.create(
            customer=user.stripe_customer_id,
            return_url=os.getenv("STRIPE_PORTAL_RETURN_URL"),
        )
        return jsonify({"url": portal_session.url})
    except Exception as e:
        print("Stripe portal error:", e)
        return jsonify({"error": "Failed to create portal session"}), 500


# ---------------------------------------------------------
# SUBSCRIPTION WEBHOOK
# ---------------------------------------------------------
@stripe_subscriptions_bp.route("/subscriptions-webhook", methods=["POST"])
def subscriptions_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, SUBS_WEBHOOK_SECRET
        )
    except Exception as e:
        print("Stripe subscriptions webhook signature error:", e)
        return jsonify({"error": "Invalid signature"}), 400

    event_type = event["type"]
    data_obj = event["data"]["object"]

    # Helper: find user by Stripe customer
    def get_user_by_customer(customer_id: str):
        if not customer_id:
            return None
        return User.query.filter_by(stripe_customer_id=customer_id).first()

    # -----------------------------
    # SUBSCRIPTION CREATED / UPDATED
    # -----------------------------
    if event_type in (
        "customer.subscription.created",
        "customer.subscription.updated",
    ):
        sub = data_obj
        customer_id = sub.get("customer")
        status = sub.get("status")
        stripe_sub_id = sub.get("id")

        user = get_user_by_customer(customer_id)
        if not user:
            return "", 200

        # Determine plan from price
        items = sub.get("items", {}).get("data", [])
        plan_name = None
        if items:
            price_id = items[0]["price"]["id"]
            for name, pid in PLAN_PRICE_IDS.items():
                if pid == price_id:
                    plan_name = name
                    break

        if not plan_name:
            print("Unknown subscription price, skipping plan sync")
            return "", 200

        if status in ("active", "trialing"):
            apply_plan_to_user(user, plan_name, stripe_sub_id=stripe_sub_id)
            db.session.commit()
        elif status in ("canceled", "unpaid", "incomplete_expired", "past_due"):
            # Mark subscriptions inactive, keep user on Free
            Subscription.query.filter_by(user_id=user.id, active=True).update(
                {"active": False}
            )
            user.plan = "Free"
            db.session.commit()

    # -----------------------------
    # INVOICE PAYMENT SUCCEEDED
    # (Good place to log revenue + credit transaction)
    # -----------------------------
    if event_type == "invoice.payment_succeeded":
        invoice = data_obj
        customer_id = invoice.get("customer")
        amount_paid = invoice.get("amount_paid")  # in cents
        currency = invoice.get("currency")
        stripe_sub_id = invoice.get("subscription")

        user = get_user_by_customer(customer_id)
        if not user:
            return "", 200

        # Log credit transaction as subscription payment
        tx = CreditTransaction(
            user_id=user.id,
            amount=amount_paid,  # store raw amount (cents)
            type="SUBSCRIPTION_PAYMENT",
            meta_data={
                "stripe_invoice_id": invoice.get("id"),
                "stripe_subscription_id": stripe_sub_id,
                "currency": currency,
            },
            created_at=datetime.utcnow(),
        )
        db.session.add(tx)

        log_billing_event(
            user_id=user.id,
            category="subscription",
            feature="invoice_payment",
            credits_used=0,
            plan=user.plan,
            details={
                "amount_paid": amount_paid,
                "currency": currency,
                "stripe_invoice_id": invoice.get("id"),
            },
        )

        db.session.commit()

    # -----------------------------
    # SUBSCRIPTION DELETED
    # -----------------------------
    if event_type == "customer.subscription.deleted":
        sub = data_obj
        customer_id = sub.get("customer")

        user = get_user_by_customer(customer_id)
        if not user:
            return "", 200

        Subscription.query.filter_by(user_id=user.id, active=True).update(
            {"active": False}
        )
        user.plan = "Free"
        db.session.commit()

    return "", 200
