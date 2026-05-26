from database import db
from datetime import datetime

class ScheduledPromo(db.Model):
    __tablename__ = "scheduled_promos"

    id = db.Column(db.Integer, primary_key=True)

    # Where this promo will appear
    location = db.Column(db.String(50), nullable=False)  # landing, dashboard, studio

    # Content
    title = db.Column(db.String(255))
    subtitle = db.Column(db.Text)
    asset_url = db.Column(db.Text, nullable=False)
    asset_type = db.Column(db.String(20), default="image")  # image, video
    language = db.Column(db.String(50), default="English")

    # Scheduling
    scheduled_for = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default="pending")  # pending, executed, cancelled

    # Audit
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    executed_at = db.Column(db.DateTime, nullable=True)
