from models.promo_slot import PromoSlot
from database import db
from datetime import datetime

VALID_LOCATIONS = ["landing", "dashboard", "studio"]

def publish_promo(location: str, title: str, subtitle: str, asset_url: str, asset_type: str, language: str):
    if location not in VALID_LOCATIONS:
        raise ValueError("Invalid promo location")

    slot = PromoSlot.query.filter_by(location=location).first()

    if not slot:
        slot = PromoSlot(
            location=location,
            title=title,
            subtitle=subtitle,
            asset_url=asset_url,
            asset_type=asset_type,
            language=language,
            updated_at=datetime.utcnow()
        )
        db.session.add(slot)
    else:
        slot.title = title
        slot.subtitle = subtitle
        slot.asset_url = asset_url
        slot.asset_type = asset_type
        slot.language = language
        slot.updated_at = datetime.utcnow()

    db.session.commit()
    return slot


def get_promo(location: str):
    if location not in VALID_LOCATIONS:
        return None
    return PromoSlot.query.filter_by(location=location).first()
