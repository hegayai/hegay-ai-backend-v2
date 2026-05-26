import os
from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

canvas_project_delete_bp = Blueprint("canvas_project_delete_bp", __name__)

PROJECT_FOLDER = "projects"

@canvas_project_delete_bp.route("/project/delete", methods=["POST"])
def delete_project():
    project_id = request.json.get("project_id")

    if not project_id:
        return jsonify({"status": "error", "message": "project_id required"}), 400

    filename = secure_filename(f"{project_id}.json")
    file_path = os.path.join(PROJECT_FOLDER, filename)

    if not os.path.exists(file_path):
        return jsonify({"status": "error", "message": "Project not found"}), 404

    os.remove(file_path)

    return jsonify({
        "status": "success",
        "message": "Project deleted",
        "project_id": project_id
    })
