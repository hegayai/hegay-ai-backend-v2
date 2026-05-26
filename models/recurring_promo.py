from database import db
from datetime import datetime

class RecurringPromo(db.Model):
    __tablename__ = "recurring_promos"

    id = db.Column(db.Integer, primary_key=True)

    # Where it publishes
    location = db.Column(db.String(50), nullable=False)  # landing | dashboard | studio

    # Content
    title = db.Column(db.String(255))
    subtitle = db.Column(db.Text)
    asset_url = db.Column(db.Text, nullable=False)
    asset_type = db.Column(db.String(20), default="image")  # image | video
    language = db.Column(db.String(50), default="English")

    # Recurrence
    # weekly | daily | interval | monthly
    recurrence_type = db.Column(db.String(20), nullable=False)

    # weekly   → "monday", "friday"
    # daily    → "everyday" (or any placeholder)
    # interval → "7" (days)
    # monthly  → "1", "15", "last"
    recurrence_value = db.Column(db.String(50), nullable=False)

    # Tracking
    last_executed = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
