from database import db
from datetime import datetime

class PromoSlot(db.Model):
    __tablename__ = "promo_slots"

    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(50), nullable=False)  # landing, dashboard, studio
    title = db.Column(db.String(255))
    subtitle = db.Column(db.Text)
    asset_url = db.Column(db.Text)
    asset_type = db.Column(db.String(20))  # image, video
    language = db.Column(db.String(50))

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
