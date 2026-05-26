from database import db
from datetime import datetime

class ApiUsage(db.Model):
    __tablename__ = "api_usage"

    id = db.Column(db.Integer, primary_key=True)

    # Endpoint used (e.g., /creative/image-forge/generate)
    endpoint = db.Column(db.String(255), nullable=False)

    # Count of calls (middleware increments this)
    count = db.Column(db.Integer, default=1)

    # Timestamp of the call
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Optional user reference
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    user = db.relationship("User", backref="api_usage")

    # ---------------------------------------------------------
    # SAFE SERIALIZER
    # ---------------------------------------------------------
    def as_dict(self):
        return {
            "id": self.id,
            "endpoint": self.endpoint,
            "count": self.count,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "user_id": self.user_id,
            "user_email": self.user.email if self.user else None
        }
