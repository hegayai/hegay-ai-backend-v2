from models.brand_style import BrandStyle
from database import db
from datetime import datetime

def save_brand_style(user_id, data):
    brand = BrandStyle.query.filter_by(
        user_id=user_id,
        brand_name=data.get("brand_name")
    ).first()

    if brand:
        # Update existing brand
        for key, value in data.items():
            setattr(brand, key, value)
        brand.updated_at = datetime.utcnow()
    else:
        # Create new brand style
        brand = BrandStyle(user_id=user_id, **data)
        db.session.add(brand)

    db.session.commit()
    return brand


def get_brand_style(user_id, brand_name):
    return BrandStyle.query.filter_by(
        user_id=user_id,
        brand_name=brand_name
    ).first()


def get_all_brand_styles(user_id):
    return BrandStyle.query.filter_by(user_id=user_id).all()
