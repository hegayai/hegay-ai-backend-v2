from flask import Blueprint, jsonify, request, session
from database import db
from models.engine import Engine
from models.user import User
from datetime import datetime

engines_bp = Blueprint("engines_bp", __name__)

# ---------------------------------------------------------
# ADMIN AUTH CHECK
# ---------------------------------------------------------
def require_admin():
    user_id = session.get("user_id")

    if not user_id:
        return None, jsonify({"error": "Not authenticated"}), 401

    user = User.query.get(user_id)

    if not user or user.role != "admin":
        return None, jsonify({"error": "Admin access required"}), 403

    return user, None, None


# ---------------------------------------------------------
# LIST ALL ENGINES
# ---------------------------------------------------------
@engines_bp.route("/", methods=["GET"])
def list_engines():
    try:
        _, err, code = require_admin()
        if err:
            return err, code

        engines = Engine.query.order_by(Engine.id.desc()).all()

        data = []
        for e in engines:
            data.append({
                "id": e.id,
                "name": e.name,
                "display_name": e.display_name,
                "status": e.status,
                "current_model": e.current_model,
                "version": e.version,
                "gpu_usage": e.gpu_usage,
                "cpu_usage": e.cpu_usage,
                "memory_usage": e.memory_usage,
                "queue_length": e.queue_length,
                "last_heartbeat": e.last_heartbeat.isoformat() if e.last_heartbeat else None,
                "is_admin_only": e.is_admin_only
            })

        return jsonify({"engines": data})

    except Exception as e:
        print("List engines error:", e)
        return jsonify({"error": "Failed to load engines"}), 500


# ---------------------------------------------------------
# CREATE NEW ENGINE
# ---------------------------------------------------------
@engines_bp.route("/create", methods=["POST"])
def create_engine():
    try:
        _, err, code = require_admin()
        if err:
            return err, code

        data = request.json or {}

        name = data.get("name")
        display_name = data.get("display_name")
        current_model = data.get("current_model", "default")
        version = data.get("version", "v1")
        is_admin_only = data.get("is_admin_only", False)

        if not name or not display_name:
            return jsonify({"error": "Name and display_name are required"}), 400

        new_engine = Engine(
            name=name,
            display_name=display_name,
            current_model=current_model,
            version=version,
            status="stopped",
            gpu_usage=0,
            cpu_usage=0,
            memory_usage=0,
            queue_length=0,
            last_heartbeat=datetime.utcnow(),
            is_admin_only=is_admin_only
        )

        db.session.add(new_engine)
        db.session.commit()

        return jsonify({
            "message": "Engine created successfully",
            "engine_id": new_engine.id
        })

    except Exception as e:
        print("Create engine error:", e)
        return jsonify({"error": "Failed to create engine"}), 500


# ---------------------------------------------------------
# UPDATE ENGINE
# ---------------------------------------------------------
@engines_bp.route("/<int:engine_id>", methods=["PUT"])
def update_engine(engine_id):
    try:
        _, err, code = require_admin()
        if err:
            return err, code

        engine = Engine.query.get(engine_id)
        if not engine:
            return jsonify({"error": "Engine not found"}), 404

        data = request.json or {}

        engine.name = data.get("name", engine.name)
        engine.display_name = data.get("display_name", engine.display_name)
        engine.current_model = data.get("current_model", engine.current_model)
        engine.version = data.get("version", engine.version)
        engine.status = data.get("status", engine.status)
        engine.is_admin_only = data.get("is_admin_only", engine.is_admin_only)
        engine.last_heartbeat = datetime.utcnow()

        db.session.commit()

        return jsonify({"message": "Engine updated successfully"})

    except Exception as e:
        print("Update engine error:", e)
        return jsonify({"error": "Failed to update engine"}), 500


# ---------------------------------------------------------
# DELETE ENGINE
# ---------------------------------------------------------
@engines_bp.route("/<int:engine_id>", methods=["DELETE"])
def delete_engine(engine_id):
    try:
        _, err, code = require_admin()
        if err:
            return err, code

        engine = Engine.query.get(engine_id)
        if not engine:
            return jsonify({"error": "Engine not found"}), 404

        db.session.delete(engine)
        db.session.commit()

        return jsonify({"message": "Engine deleted successfully"})

    except Exception as e:
        print("Delete engine error:", e)
        return jsonify({"error": "Failed to delete engine"}), 500
