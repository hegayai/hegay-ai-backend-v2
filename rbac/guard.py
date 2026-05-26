from functools import wraps
from flask import request, jsonify
from rbac.permissions import PERMISSIONS
from models.user import User

def require_permission(permission):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token_user = request.user  # from JWT middleware

            if not token_user:
                return jsonify({"error": "Unauthorized"}), 401

            user = User.query.get(token_user["id"])
            roles = [r.name for r in user.roles]

            allowed = any(
                permission in PERMISSIONS.get(role, [])
                for role in roles
            )

            if not allowed:
                return jsonify({"error": "Forbidden"}), 403

            return f(*args, **kwargs)
        return wrapper
    return decorator
