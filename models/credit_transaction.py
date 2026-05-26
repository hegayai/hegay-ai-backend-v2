from database import db
from datetime import datetime


class CreditTransaction(db.Model):
    __tablename__ = "credit_transactions"

    id = db.Column(db.Integer, primary_key=True)

    # User who performed the transaction
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", backref="credit_transactions")

    # Positive = credits added, Negative = credits used
    amount = db.Column(db.Integer, nullable=False)

    # e.g. "CREDITS_PURCHASED", "IMAGE_GENERATION", "VIDEO_GENERATION"
    type = db.Column(db.String(100), nullable=False)

    # JSON metadata (model, tool, stripe session, tier, etc.)
    meta_data = db.Column(db.JSON, nullable=True)

    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # ---------------------------------------------------------
    # SAFE SERIALIZER
    # ---------------------------------------------------------
    def as_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_email": self.user.email if self.user else None,
            "amount": self.amount,
            "type": self.type,
            "meta_data": self.meta_data or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
