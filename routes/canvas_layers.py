import os
import json
from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

canvas_layers_bp = Blueprint("canvas_layers_bp", __name__)

LAYERS_FOLDER = "layers"
os.makedirs(LAYERS_FOLDER, exist_ok=True)


def layers_file(project_id):
    filename = secure_filename(f"{project_id}_layers.json")
    return os.path.join(LAYERS_FOLDER, filename)


@canvas_layers_bp.route("/layers/init", methods=["POST"])
def init_layers():
    project_id = request.json.get("project_id")
    elements = request.json.get("elements", [])

    if not project_id:
        return jsonify({"status": "error", "message": "project_id required"}), 400

    file_path = layers_file(project_id)

    layers = []
    for index, el in enumerate(elements):
        layers.append({
            "id": el.get("id"),
            "order": index,
            "locked": False,
            "visible": True,
            "group": None
        })

    with open(file_path, "w") as f:
        json.dump(layers, f, indent=2)

    return jsonify({
        "status": "success",
        "message": "Layers initialized",
        "count": len(layers)
    })


@canvas_layers_bp.route("/layers/<project_id>", methods=["GET"])
def get_layers(project_id):
    file_path = layers_file(project_id)

    if not os.path.exists(file_path):
        return jsonify({"status": "success", "layers": []})

    with open(file_path, "r") as f:
        layers = json.load(f)

    return jsonify({
        "status": "success",
        "layers": layers
    })


@canvas_layers_bp.route("/layers/update", methods=["POST"])
def update_layer():
    project_id = request.json.get("project_id")
    layer_id = request.json.get("layer_id")
    updates = request.json.get("updates", {})

    file_path = layers_file(project_id)

    if not os.path.exists(file_path):
        return jsonify({"status": "error", "message": "No layers found"}), 404

    with open(file_path, "r") as f:
        layers = json.load(f)

    for layer in layers:
        if layer["id"] == layer_id:
            for key, value in updates.items():
                layer[key] = value

    with open(file_path, "w") as f:
        json.dump(layers, f, indent=2)

    return jsonify({
        "status": "success",
        "message": "Layer updated",
        "layer_id": layer_id
    })


@canvas_layers_bp.route("/layers/reorder", methods=["POST"])
def reorder_layers():
    project_id = request.json.get("project_id")
    order = request.json.get("order", [])

    file_path = layers_file(project_id)

    if not os.path.exists(file_path):
        return jsonify({"status": "error", "message": "No layers found"}), 404

    with open(file_path, "r") as f:
        layers = json.load(f)

    # Apply new order
    for index, layer_id in enumerate(order):
        for layer in layers:
            if layer["id"] == layer_id:
                layer["order"] = index

    with open(file_path, "w") as f:
        json.dump(layers, f, indent=2)

    return jsonify({
        "status": "success",
        "message": "Layers reordered"
    })


@canvas_layers_bp.route("/layers/group", methods=["POST"])
def group_layers():
    project_id = request.json.get("project_id")
    layer_ids = request.json.get("layer_ids", [])
    group_id = request.json.get("group_id")

    file_path = layers_file(project_id)

    if not os.path.exists(file_path):
        return jsonify({"status": "error", "message": "No layers found"}), 404

    with open(file_path, "r") as f:
        layers = json.load(f)

    for layer in layers:
        if layer["id"] in layer_ids:
            layer["group"] = group_id

    with open(file_path, "w") as f:
        json.dump(layers, f, indent=2)

    return jsonify({
        "status": "success",
        "message": "Layers grouped",
        "group_id": group_id
    })


@canvas_layers_bp.route("/layers/ungroup", methods=["POST"])
def ungroup_layers():
    project_id = request.json.get("project_id")
    group_id = request.json.get("group_id")

    file_path = layers_file(project_id)

    if not os.path.exists(file_path):
        return jsonify({"status": "error", "message": "No layers found"}), 404

    with open(file_path, "r") as f:
        layers = json.load(f)

    for layer in layers:
        if layer["group"] == group_id:
            layer["group"] = None

    with open(file_path, "w") as f:
        json.dump(layers, f, indent=2)

    return jsonify({
        "status": "success",
        "message": "Layers ungrouped",
        "group_id": group_id
    })
