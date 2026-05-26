from database import db
from datetime import datetime

class SecurityLog(db.Model):
    __tablename__ = "security_logs"

    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(255), nullable=False)
    actor = db.Column(db.String(255), nullable=False)
    ip = db.Column(db.String(100))
    user_agent = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
