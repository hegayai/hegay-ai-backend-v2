from datetime import datetime
from database import db
from models.scheduled_promo import ScheduledPromo
from utils.auto_publish_engine import publish_promo

def schedule_promo(location, title, subtitle, asset_url, asset_type, language, scheduled_for):
    promo = ScheduledPromo(
        location=location,
        title=title,
        subtitle=subtitle,
        asset_url=asset_url,
        asset_type=asset_type,
        language=language,
        scheduled_for=scheduled_for,
        status="pending"
    )
    db.session.add(promo)
    db.session.commit()
    return promo


def run_due_schedules():
    now = datetime.utcnow()

    due_promos = (
        ScheduledPromo.query
        .filter(ScheduledPromo.status == "pending")
        .filter(ScheduledPromo.scheduled_for <= now)
        .all()
    )

    executed = []

    for sp in due_promos:
        publish_promo(
            location=sp.location,
            title=sp.title or "",
            subtitle=sp.subtitle or "",
            asset_url=sp.asset_url,
            asset_type=sp.asset_type,
            language=sp.language
        )

        sp.status = "executed"
        sp.executed_at = now
        executed.append(sp)

    if executed:
        db.session.commit()

    return executed
