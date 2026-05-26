from flask import Blueprint, jsonify, request, Response, stream_with_context
import json
import time

from utils.engine_manager import (
    init_engines,
    get_engines,
    set_engine_status,
    switch_engine_model,
    heartbeat_all_engines,
)

engines_bp = Blueprint("engines_bp", __name__)

# Ensure engines exist at import time (safe if called multiple times)
@engines_bp.before_app_request
def _ensure_engines():
    init_engines()


def _serialize_engine(e):
    return {
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
        "is_admin_only": e.is_admin_only,
    }


# ---------------------------------------------------------
# ⭐ LIST ENGINES
# ---------------------------------------------------------
@engines_bp.route("/list", methods=["GET"])
def list_engines():
    engines = get_engines()
    return jsonify({
        "engines": [_serialize_engine(e) for e in engines]
    }), 200


# ---------------------------------------------------------
# ⭐ START ENGINE
# ---------------------------------------------------------
@engines_bp.route("/start/<int:engine_id>", methods=["POST"])
def start_engine(engine_id):
    e = set_engine_status(engine_id, "running")
    if not e:
        return jsonify({"error": "Engine not found"}), 404
    return jsonify({"message": "Engine started", "engine": _serialize_engine(e)}), 200


# ---------------------------------------------------------
# ⭐ STOP ENGINE
# ---------------------------------------------------------
@engines_bp.route("/stop/<int:engine_id>", methods=["POST"])
def stop_engine(engine_id):
    e = set_engine_status(engine_id, "stopped")
    if not e:
        return jsonify({"error": "Engine not found"}), 404
    return jsonify({"message": "Engine stopped", "engine": _serialize_engine(e)}), 200


# ---------------------------------------------------------
# ⭐ RESTART ENGINE
# ---------------------------------------------------------
@engines_bp.route("/restart/<int:engine_id>", methods=["POST"])
def restart_engine(engine_id):
    e = set_engine_status(engine_id, "running")
    if not e:
        return jsonify({"error": "Engine not found"}), 404
    return jsonify({"message": "Engine restarted", "engine": _serialize_engine(e)}), 200


# ---------------------------------------------------------
# ⭐ SWITCH MODEL
# ---------------------------------------------------------
@engines_bp.route("/switch-model/<int:engine_id>", methods=["POST"])
def switch_model(engine_id):
    data = request.get_json() or {}
    model_name = data.get("model_name", "default")
    version = data.get("version")
    e = switch_engine_model(engine_id, model_name, version)
    if not e:
        return jsonify({"error": "Engine not found"}), 404
    return jsonify({"message": "Model switched", "engine": _serialize_engine(e)}), 200


# ---------------------------------------------------------
# ⭐ SSE: ENGINE HEALTH STREAM
# ---------------------------------------------------------
@engines_bp.route("/stream", methods=["GET"])
def engines_stream():
    @stream_with_context
    def event_stream():
        while True:
            engines = heartbeat_all_engines()
            payload = {
                "engines": [_serialize_engine(e) for e in engines]
            }
            yield f"data: {json.dumps(payload)}\n\n"
            time.sleep(3)

    return Response(event_stream(), mimetype="text/event-stream")
