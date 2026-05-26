import os
from flask import jsonify
from dotenv import load_dotenv

from db import SessionLocal
from models import User, Role, UserRole

load_dotenv()

def register_bootstrap_route(app):
    @app.route("/bootstrap-admin", methods=["POST"])
    def bootstrap_admin():
        admin_email = os.getenv("ADMIN_EMAIL", "admin@hegay.ai")
        admin_password = os.getenv("ADMIN_PASSWORD", "ChangeThisAdminPassword!")

        db = SessionLocal()
        try:
            existing_admin = db.query(User).filter(User.email == admin_email).first()
            if existing_admin:
                return jsonify({"message": "Admin already exists"}), 200

            admin_role = db.query(Role).filter(Role.name == "admin").first()
            if not admin_role:
                admin_role = Role(name="admin")
                db.add(admin_role)
                db.commit()
                db.refresh(admin_role)

            admin_user = User(email=admin_email)
            admin_user.set_password(admin_password)
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)

            link = UserRole(user_id=admin_user.id, role_id=admin_role.id)
            db.add(link)
            db.commit()

            return jsonify({
                "message": "Admin user created",
                "admin_email": admin_email,
                "admin_role": "admin"
            }), 201
        finally:
            db.close()
