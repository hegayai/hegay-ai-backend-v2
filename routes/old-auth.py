from flask import Blueprint, request, jsonify
from db import SessionLocal
from models import User, Role
from jwt_utils import create_access_token, create_refresh_token

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    db = SessionLocal()
    try:
        existing = db.query(User).filter_by(email=email).first()
        if existing:
            return jsonify({"error": "User already exists"}), 400

        user = User(email=email, is_active=True)
        user.set_password(password)
        db.add(user)
        db.commit()

        role = db.query(Role).filter_by(name="creator").first()
        if not role:
            role = Role(name="creator")
            db.add(role)
            db.commit()

        user.roles.append(role)
        db.commit()

        return jsonify({"message": "User registered successfully"}), 201
    finally:
        db.close()


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    db = SessionLocal()
    try:
        user = db.query(User).filter_by(email=email).first()
        if not user or not user.check_password(password):
            return jsonify({"error": "Invalid credentials"}), 401

        role_names = [r.name for r in user.roles]

        access_token = create_access_token(user.id, role_names)
        refresh_token = create_refresh_token(user.id)

        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "email": user.email,
            "roles": role_names
        }), 200
    finally:
        db.close()
