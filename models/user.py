from database import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # ---------------------------------------------------------
    # ⭐ PREMIUM USER FIELDS (SAFE DEFAULTS)
    # ---------------------------------------------------------
    name = db.Column(db.String(255), nullable=True)

    # Subscription plan (Free, Pro, Enterprise, Admin override)
    plan = db.Column(db.String(50), default="Free")

    # Credits system
    credits_total = db.Column(db.Integer, default=50)
    credits_used = db.Column(db.Integer, default=0)

    # User role (user, admin, superadmin)
    role = db.Column(db.String(50), default="user")

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    # ---------------------------------------------------------
    # ⭐ CREDIT CALCULATION (SAFE)
    # ---------------------------------------------------------
    @property
    def credits_remaining(self):
        total = self.credits_total or 0
        used = self.credits_used or 0
        return max(total - used, 0)

    # ---------------------------------------------------------
    # ⭐ PASSWORD MANAGEMENT
    # ---------------------------------------------------------
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
