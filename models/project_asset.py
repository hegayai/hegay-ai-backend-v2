from database import db
from datetime import datetime

class ProjectAsset(db.Model):
    __tablename__ = "project_assets"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # image, video, motion
    url = db.Column(db.Text, nullable=False)

    # Renamed from "metadata" → "data" (SQLAlchemy reserved word fix)
    data = db.Column(db.JSON)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
