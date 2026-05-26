from database import db
from main import app

# Import ALL models so SQLAlchemy knows them
from models.user import User
from models.role import Role
from models.user_role import UserRole
from models.api_key import ApiKey
from models.api_usage import ApiUsage
from models.engine import Engine
from models.scheduled_promo import ScheduledPromo
from models.recurring_promo import RecurringPromo
from models.project_asset import ProjectAsset

with app.app_context():
    print("Creating all tables...")
    db.create_all()
    print("DONE — All tables created successfully.")
