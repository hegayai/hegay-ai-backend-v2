from database import db
from models.user import User
from datetime import datetime

def seed_admin():
    admin_email = "admin@hegay.ai"
    admin_password = "Admin@162000@"

    # Check if admin already exists
    existing = User.query.filter_by(email=admin_email).first()

    if existing:
        print("✔ Admin user already exists.")
        return

    print("⚠ Admin user missing — creating new admin...")

    # Create admin user
    admin = User(
        email=admin_email,
        role="admin",
        created_at=datetime.utcnow()
    )
    admin.set_password(admin_password)

    db.session.add(admin)
    db.session.commit()

    print("✔ Admin user created successfully.")
