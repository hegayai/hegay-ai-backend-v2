from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class FeatureFlag(db.Model):
    __tablename__ = "feature_flags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))
    enabled = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PlanConfig(db.Model):
    __tablename__ = "plan_configs"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    label = db.Column(db.String(100))
    price_gbp = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    is_promo = db.Column(db.Boolean, default=False)

    images = db.Column(db.Integer, default=0)
    videos = db.Column(db.Integer, default=0)
    max_video_seconds = db.Column(db.Integer, default=0)
    canvas_limit = db.Column(db.Integer, default=0)
    chat_messages = db.Column(db.Integer, default=0)
    max_resolution = db.Column(db.String(20), default="720p")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ModelCatalog(db.Model):
    __tablename__ = "model_catalog"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    label = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(255))

    base_credits = db.Column(db.Integer, default=0)
    base_seconds = db.Column(db.Integer)
    base_resolution = db.Column(db.String(20))

    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ResolutionConfig(db.Model):
    __tablename__ = "resolution_configs"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    multiplier = db.Column(db.Float, default=1.0)
    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DurationTier(db.Model):
    __tablename__ = "duration_tiers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    seconds = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
