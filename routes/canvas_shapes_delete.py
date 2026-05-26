import os
from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

canvas_shapes_delete_bp = Blueprint("canvas_shapes_delete_bp", __name__)

SHAPES_FOLDER = "shapes"

@canvas_shapes_delete_bp.route("/shapes/delete", methods=["POST"])
def delete_shape():
    shape_id = request.json.get("shape_id")

    if not shape_id:
        return jsonify({"status": "error", "message": "shape_id required"}), 400

    filename = secure_filename(f"{shape_id}.json")
    file_path = os.path.join(SHAPES_FOLDER, filename)

    if not os.path.exists(file_path):
        return jsonify({"status": "error", "message": "Shape not found"}), 404

    os.remove(file_path)

    return jsonify({
        "status": "success",
        "message": "Shape deleted",
        "shape_id": shape_id
    })
