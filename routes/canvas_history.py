import os
import json
from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

canvas_history_bp = Blueprint("canvas_history_bp", __name__)

HISTORY_FOLDER = "history"
os.makedirs(HISTORY_FOLDER, exist_ok=True)


def history_file(project_id):
    filename = secure_filename(f"{project_id}_history.json")
    return os.path.join(HISTORY_FOLDER, filename)


@canvas_history_bp.route("/history/push", methods=["POST"])
def push_history():
    project_id = request.json.get("project_id")
    state = request.json.get("state", {})

    if not project_id:
        return jsonify({"status": "error", "message": "project_id required"}), 400

    file_path = history_file(project_id)

    # Load existing history
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            history = json.load(f)
    else:
        history = {"undo": [], "redo": []}

    # Push new state to undo stack
    history["undo"].append(state)
    history["redo"] = []  # Clear redo stack on new action

    with open(file_path, "w") as f:
        json.dump(history, f, indent=2)

    return jsonify({
        "status": "success",
        "message": "State pushed to history",
        "undo_count": len(history["undo"])
    })


@canvas_history_bp.route("/history/undo/<project_id>", methods=["GET"])
def undo(project_id):
    file_path = history_file(project_id)

    if not os.path.exists(file_path):
        return jsonify({"status": "error", "message": "No history found"}), 404

    with open(file_path, "r") as f:
        history = json.load(f)

    if not history["undo"]:
        return jsonify({"status": "error", "message": "Nothing to undo"}), 400

    # Pop last state
    state = history["undo"].pop()
    history["redo"].append(state)

    with open(file_path, "w") as f:
        json.dump(history, f, indent=2)

    return jsonify({
        "status": "success",
        "state": state,
        "undo_count": len(history["undo"]),
        "redo_count": len(history["redo"])
    })


@canvas_history_bp.route("/history/redo/<project_id>", methods=["GET"])
def redo(project_id):
    file_path = history_file(project_id)

    if not os.path.exists(file_path):
        return jsonify({"status": "error", "message": "No history found"}), 404

    with open(file_path, "r") as f:
        history = json.load(f)

    if not history["redo"]:
        return jsonify({"status": "error", "message": "Nothing to redo"}), 400

    # Pop from redo stack
    state = history["redo"].pop()
    history["undo"].append(state)

    with open(file_path, "w") as f:
        json.dump(history, f, indent=2)

    return jsonify({
        "status": "success",
        "state": state,
        "undo_count": len(history["undo"]),
        "redo_count": len(history["redo"])
    })
