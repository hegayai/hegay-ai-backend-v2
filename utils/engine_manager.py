import random
import time
from datetime import datetime
from database import db
from models.engine import Engine

ENGINE_DEFS = [
    {
        "name": "image",
        "display_name": "Image Engine",
        "is_admin_only": False,
    },
    {
        "name": "video",
        "display_name": "Video Engine",
        "is_admin_only": False,
    },
    {
        "name": "motion",
        "display_name": "Motion Engine",
        "is_admin_only": True,  # Admin‑only for now
    },
]


def init_engines():
    """Ensure default engines exist."""
    for cfg in ENGINE_DEFS:
        existing = Engine.query.filter_by(name=cfg["name"]).first()
        if not existing:
            e = Engine(
                name=cfg["name"],
                display_name=cfg["display_name"],
                is_admin_only=cfg["is_admin_only"],
                status="stopped",
                current_model="default",
                version="v1",
            )
            db.session.add(e)
    db.session.commit()


def get_engines():
    return Engine.query.order_by(Engine.id.asc()).all()


def set_engine_status(engine_id: int, status: str):
    engine = Engine.query.get(engine_id)
    if not engine:
        return None
    engine.status = status
    engine.last_heartbeat = datetime.utcnow()
    if status == "running":
        # when starting, reset queue a bit
        engine.queue_length = max(engine.queue_length, 0)
    db.session.commit()
    return engine


def switch_engine_model(engine_id: int, model_name: str, version: str | None = None):
    engine = Engine.query.get(engine_id)
    if not engine:
        return None
    engine.current_model = model_name
    if version:
        engine.version = version
    engine.last_heartbeat = datetime.utcnow()
    db.session.commit()
    return engine


def simulate_engine_metrics(engine: Engine):
    """Dev‑mode simulation of GPU/CPU/memory/queue."""
    if engine.status != "running":
        engine.gpu_usage = 0
        engine.cpu_usage = 0
        engine.memory_usage = max(engine.memory_usage - 10, 0)
        engine.queue_length = max(engine.queue_length - 1, 0)
    else:
        engine.gpu_usage = min(max(engine.gpu_usage + random.randint(-10, 15), 5), 95)
        engine.cpu_usage = min(max(engine.cpu_usage + random.randint(-8, 12), 5), 95)
        engine.memory_usage = max(engine.memory_usage + random.randint(-20, 40), 50)
        engine.queue_length = max(engine.queue_length + random.randint(-1, 3), 0)

    engine.last_heartbeat = datetime.utcnow()
    db.session.commit()
    return engine


def heartbeat_all_engines():
    """Update metrics for all engines (used by SSE stream)."""
    engines = Engine.query.all()
    updated = []
    for e in engines:
        updated.append(simulate_engine_metrics(e))
    return updated
