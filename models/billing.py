from datetime import datetime
from database import db


class BillingEvent(db.Model):
    __tablename__ = "billing_events"

    id = db.Column(db.Integer, primary_key=True)

    # User who triggered the event
    user_id = db.Column(db.Integer, nullable=False)

    # User's plan at the time of the event (Free, Starter, Creator, Pro, Studio)
    plan = db.Column(db.String(50), nullable=True)

    # Category A or B
    category = db.Column(db.String(10), nullable=False)

    # Feature used (e.g., "text_to_image", "music_generator_pro")
    feature = db.Column(db.String(100), nullable=False)

    # Credits spent
    credits_used = db.Column(db.Integer, default=0)

    # JSON metadata (tier, duration, resolution, etc.)
    details = db.Column(db.JSON, nullable=True)

    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # ---------------------------------------------------------
    # SAFE SERIALIZER
    # ---------------------------------------------------------
    def as_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "plan": self.plan,
            "category": self.category,
            "feature": self.feature,
            "credits_used": self.credits_used,
            "details": self.details or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
