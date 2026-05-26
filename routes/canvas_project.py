import os
import json
from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

canvas_project_bp = Blueprint("canvas_project_bp", __name__)

PROJECT_FOLDER = "projects"
os.makedirs(PROJECT_FOLDER, exist_ok=True)


@canvas_project_bp.route("/project/save", methods=["POST"])
def save_project():
    project_id = request.json.get("project_id")
    elements = request.json.get("elements", [])
    metadata = request.json.get("metadata", {})

    if not project_id:
        return jsonify({"status": "error", "message": "project_id required"}), 400

    filename = secure_filename(f"{project_id}.json")
    save_path = os.path.join(PROJECT_FOLDER, filename)

    with open(save_path, "w") as f:
        json.dump({
            "project_id": project_id,
            "elements": elements,
            "metadata": metadata
        }, f, indent=2)

    return jsonify({
        "status": "success",
        "message": "Project saved",
        "project_id": project_id
    })


@canvas_project_bp.route("/project/load/<project_id>", methods=["GET"])
def load_project(project_id):
    filename = secure_filename(f"{project_id}.json")
    file_path = os.path.join(PROJECT_FOLDER, filename)

    if not os.path.exists(file_path):
        return jsonify({"status": "error", "message": "Project not found"}), 404

    with open(file_path, "r") as f:
        data = json.load(f)

    return jsonify({
        "status": "success",
        "project": data
    })


@canvas_project_bp.route("/project/list", methods=["GET"])
def list_projects():
    files = os.listdir(PROJECT_FOLDER)
    projects = [f.replace(".json", "") for f in files if f.endswith(".json")]

    return jsonify({
        "status": "success",
        "projects": projects
    })
