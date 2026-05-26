from database import db
from models.user import User
from models.role import Role
from models.user_role import UserRole
from flask import Flask

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:password@localhost:5432/hegay"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    # Create tables if missing
    db.create_all()

    # Create admin role if missing
    admin_role = Role.query.filter_by(name="admin").first()
    if not admin_role:
        admin_role = Role(name="admin")
        db.session.add(admin_role)
        db.session.commit()

    # Create admin user
    user = User.query.filter_by(email="admin@hegay.ai").first()
    if not user:
        user = User(email="admin@hegay.ai")
        user.set_password("Admin@162000@")
        db.session.add(user)
        db.session.commit()

    # Assign role
    if admin_role not in user.roles:
        user.roles.append(admin_role)
        db.session.commit()

    print("Admin user created successfully!")
