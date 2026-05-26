from flask import session, jsonify

def require_role(role_name):
    def wrapper():
        # ⭐ Correct: your session stores "role", not "roles"
        user_role = session.get("role")

        if not user_role:
            return jsonify({"error": "Unauthorized"}), 401

        if user_role != role_name:
            return jsonify({"error": "Forbidden"}), 403

        # ⭐ No session hijack checks (you never set ip/agent)
        return None

    return wrapper
