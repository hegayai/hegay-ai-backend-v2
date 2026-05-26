from database import db
from datetime import datetime

class BrandStyle(db.Model):
    __tablename__ = "brand_styles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)

    brand_name = db.Column(db.String(200), nullable=False)
    logo_url = db.Column(db.Text)
    primary_color = db.Column(db.String(20))
    secondary_color = db.Column(db.String(20))
    accent_color = db.Column(db.String(20))

    font_family = db.Column(db.String(100))
    font_weight = db.Column(db.String(50))
    font_style = db.Column(db.String(50))

    design_language = db.Column(db.String(200))
    tone = db.Column(db.String(200))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
