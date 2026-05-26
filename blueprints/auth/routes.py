from flask import Blueprint, request, jsonify, session
from database import db
from models.user import User
from flask_wtf.csrf import CSRFProtect

auth_bp = Blueprint("auth_bp", __name__)
csrf = CSRFProtect()

# ---------------------------------------------------------
# ⭐ LOGIN
# ---------------------------------------------------------
@auth_bp.route("/login", methods=["POST"])
@csrf.exempt
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    session.clear()
    session["user_id"] = user.id
    session["email"] = user.email
    session["roles"] = [role.name for role in user.roles]
    session["ip"] = request.remote_addr
    session["agent"] = request.headers.get("User-Agent")

    return jsonify({"message": "Login successful"}), 200

# ---------------------------------------------------------
# ⭐ LOGOUT
# ---------------------------------------------------------
@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"}), 200

# ---------------------------------------------------------
# ⭐ CURRENT USER (SESSION CHECK)
# ---------------------------------------------------------
@auth_bp.route("/me", methods=["GET"])
def me():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    # Optional: session hijack protection
    if session.get("ip") != request.remote_addr:
        session.clear()
        return jsonify({"error": "Session hijack detected"}), 401

    if session.get("agent") != request.headers.get("User-Agent"):
        session.clear()
        return jsonify({"error": "Session mismatch"}), 401

    return jsonify({
        "user_id": session["user_id"],
        "email": session["email"],
        "roles": session["roles"]
    }), 200
