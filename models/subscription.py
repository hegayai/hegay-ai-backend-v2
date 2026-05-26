from database import db
from datetime import datetime

class Subscription(db.Model):
    __tablename__ = "subscriptions"

    id = db.Column(db.Integer, primary_key=True)

    # Plan at the time of subscription (Free, Starter, Creator, Pro, Studio)
    plan = db.Column(db.String(50), nullable=False)

    # Whether the subscription is currently active
    active = db.Column(db.Boolean, default=True)

    # Billing cycle timestamps
    start_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)
    renewed_at = db.Column(db.DateTime, nullable=True)

    # User relationship
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", backref="subscriptions")

    # ---------------------------------------------------------
    # SAFE SERIALIZER
    # ---------------------------------------------------------
    def as_dict(self):
        return {
            "id": self.id,
            "plan": self.plan,
            "active": self.active,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "renewed_at": self.renewed_at.isoformat() if self.renewed_at else None,
            "user_id": self.user_id,
            "user_email": self.user.email if self.user else None
        }
