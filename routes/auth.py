from flask import Blueprint, request, jsonify, session
from database import db
from models.user import User
from datetime import datetime
from functools import wraps

auth = Blueprint("auth", __name__)

# ---------------------------------------------------------
# ⭐ AUTH DECORATORS
# ---------------------------------------------------------

def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        user = User.query.get(user_id)
        if not user:
            session.clear()
            return jsonify({"error": "Unauthorized"}), 401

        # Attach user to request for downstream use
        request.user = user
        return f(*args, **kwargs)
    return wrapper


def require_role(role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user_id = session.get("user_id")
            if not user_id:
                return jsonify({"error": "Unauthorized"}), 401

            user = User.query.get(user_id)
            if not user or user.role != role:
                return jsonify({"error": "Forbidden"}), 403

            request.user = user
            return f(*args, **kwargs)
        return wrapper
    return decorator


# ---------------------------------------------------------
# ⭐ REGISTER
# ---------------------------------------------------------
@auth.post("/register")
def register():
    print("REGISTER ROUTE HIT")

    try:
        data = request.get_json()
        print("REGISTER DATA:", data)
    except Exception:
        return jsonify({"error": "Invalid JSON"}), 400

    if not data:
        return jsonify({"error": "Invalid request"}), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing fields"}), 400

    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({"error": "Email already exists"}), 400

    user = User(
        email=email,
        created_at=datetime.utcnow()
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


# ---------------------------------------------------------
# ⭐ LOGIN
# ---------------------------------------------------------
@auth.post("/login")
def login():
    print("LOGIN ROUTE HIT")

    try:
        data = request.get_json()
        print("LOGIN DATA:", data)
    except Exception:
        return jsonify({"error": "Invalid JSON"}), 400

    if not data:
        return jsonify({"error": "Invalid request"}), 400

    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    # ⭐ Make session persistent
    session.permanent = True

    # ⭐ Store session
    session["user_id"] = user.id
    session["role"] = user.role

    return jsonify({
        "message": "Logged in",
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }
    }), 200


# ---------------------------------------------------------
# ⭐ LOGOUT
# ---------------------------------------------------------
@auth.post("/logout")
def logout():
    session.clear()
    return jsonify({"message": "Logged out"}), 200


# ---------------------------------------------------------
# ⭐ AUTH CHECK
# ---------------------------------------------------------
@auth.get("/me")
@require_auth
def me():
    user = request.user

    return jsonify({
        "id": user.id,
        "email": user.email,
        "role": user.role
    }), 200
