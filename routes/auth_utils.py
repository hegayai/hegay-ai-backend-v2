import os
import jwt
import datetime
from flask import request, jsonify
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_HOURS = 2
REFRESH_TOKEN_EXPIRE_DAYS = 30

if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET is not set in .env")


# ---------------------------------------------------------
# TOKEN CREATION
# ---------------------------------------------------------

def create_access_token(user_id, roles):
    payload = {
        "sub": user_id,
        "roles": roles,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id):
    payload = {
        "sub": user_id,
        "type": "refresh",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


# ---------------------------------------------------------
# TOKEN DECODING / VERIFICATION
# ---------------------------------------------------------

def decode_token(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def verify_access_token(token: str):
    """
    Verify and decode an access token.
    Returns decoded payload or None.
    """
    return decode_token(token)


# ---------------------------------------------------------
# AUTH DECORATORS
# ---------------------------------------------------------

def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"error": "Missing Authorization header"}), 401

        token = auth_header.replace("Bearer ", "").strip()
        decoded = verify_access_token(token)

        if not decoded:
            return jsonify({"error": "Invalid or expired token"}), 401

        request.user = decoded
        return f(*args, **kwargs)

    return wrapper


def require_role(role_name):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            decoded = getattr(request, "user", None)

            if not decoded:
                return jsonify({"error": "Unauthorized"}), 401

            if role_name not in decoded.get("roles", []):
                return jsonify({"error": "Forbidden"}), 403

            return f(*args, **kwargs)

        return wrapper
    return decorator
