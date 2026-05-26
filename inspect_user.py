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
    user = User.query.filter_by(email="admin@hegay.ai").first()

    if not user:
        print("Admin user not found.")
    else:
        print("ID:", user.id)
        print("Email:", user.email)
        print("Stored hash:", user.password_hash)
