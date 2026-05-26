from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from models.user import User
from database import db

users_bp = Blueprint("users", __name__)

# ---------------------------------------------------------
# ⭐ Create a new user
# ---------------------------------------------------------
@users_bp.route("/create", methods=["POST"])
def create_user():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")
    roles = data.get("roles", ["user"])

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    # Check if user exists
    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({"error": "User already exists"}), 409

    new_user = User(
        email=email,
        password_hash=generate_password_hash(password),
        roles=roles
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created", "user": new_user.to_dict()}), 201


# ---------------------------------------------------------
# ⭐ List all users
# ---------------------------------------------------------
@users_bp.route("/list", methods=["GET"])
def list_users():
    users = User.query.order_by(User.id.asc()).all()
    return jsonify([u.to_dict() for u in users]), 200


# ---------------------------------------------------------
# ⭐ Get a single user by ID
# ---------------------------------------------------------
@users_bp.route("/get/<int:id>", methods=["GET"])
def get_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user.to_dict()), 200


# ---------------------------------------------------------
# ⭐ Search users by email
# ---------------------------------------------------------
@users_bp.route("/search", methods=["GET"])
def search_users():
    q = request.args.get("q", "")

    users = User.query.filter(User.email.ilike(f"%{q}%")).all()
    return jsonify([u.to_dict() for u in users]), 200


# ---------------------------------------------------------
# ⭐ Update user role(s)
# ---------------------------------------------------------
@users_bp.route("/update-role/<int:id>", methods=["PUT"])
def update_role(id):
    data = request.get_json()
    roles = data.get("roles")

    if not roles:
        return jsonify({"error": "Roles required"}), 400

    user = User.query.get(id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.roles = roles
    db.session.commit()

    return jsonify({"message": "Roles updated", "user": user.to_dict()}), 200


# ---------------------------------------------------------
# ⭐ Delete a user
# ---------------------------------------------------------
@users_bp.route("/delete/<int:id>", methods=["DELETE"])
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "User deleted"}), 200
