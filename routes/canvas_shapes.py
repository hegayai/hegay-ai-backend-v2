import os
import json
from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

canvas_shapes_bp = Blueprint("canvas_shapes_bp", __name__)

SHAPES_FOLDER = "shapes"
os.makedirs(SHAPES_FOLDER, exist_ok=True)


# Default built‑in shapes
DEFAULT_SHAPES = [
    {
        "id": "rect",
        "name": "Rectangle",
        "type": "shape",
        "svg": None,
        "props": {
            "radius": 0
        }
    },
    {
        "id": "rounded-rect",
        "name": "Rounded Rectangle",
        "type": "shape",
        "svg": None,
        "props": {
            "radius": 20
        }
    },
    {
        "id": "circle",
        "name": "Circle",
        "type": "shape",
        "svg": None,
        "props": {}
    },
    {
        "id": "triangle",
        "name": "Triangle",
        "type": "svg",
        "svg": "<svg viewBox='0 0 100 100'><polygon points='50,10 90,90 10,90' fill='currentColor'/></svg>",
        "props": {}
    },
    {
        "id": "star",
        "name": "Star",
        "type": "svg",
        "svg": "<svg viewBox='0 0 100 100'><polygon points='50,5 61,39 98,39 67,59 78,92 50,72 22,92 33,59 2,39 39,39' fill='currentColor'/></svg>",
        "props": {}
    }
]


@canvas_shapes_bp.route("/shapes", methods=["GET"])
def list_shapes():
    shapes = DEFAULT_SHAPES.copy()

    # Load custom shapes from folder
    for f in os.listdir(SHAPES_FOLDER):
        if f.endswith(".json"):
            with open(os.path.join(SHAPES_FOLDER, f), "r") as file:
                data = json.load(file)
                shapes.append(data)

    return jsonify({
        "status": "success",
        "shapes": shapes
    })


@canvas_shapes_bp.route("/shapes/upload", methods=["POST"])
def upload_shape():
    shape_id = request.json.get("id")
    name = request.json.get("name")
    svg = request.json.get("svg")
    props = request.json.get("props", {})

    if not shape_id or not name or not svg:
        return jsonify({"status": "error", "message": "id, name, and svg required"}), 400

    filename = secure_filename(f"{shape_id}.json")
    save_path = os.path.join(SHAPES_FOLDER, filename)

    with open(save_path, "w") as f:
        json.dump({
            "id": shape_id,
            "name": name,
            "type": "svg",
            "svg": svg,
            "props": props
        }, f, indent=2)

    return jsonify({
        "status": "success",
        "message": "Shape uploaded",
        "shape_id": shape_id
    })


@canvas_shapes_bp.route("/shapes/<shape_id>", methods=["GET"])
def load_shape(shape_id):
    filename = secure_filename(f"{shape_id}.json")
    file_path = os.path.join(SHAPES_FOLDER, filename)

    # Check custom shapes
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
        return jsonify({
            "status": "success",
            "shape": data
        })

    # Check built‑in shapes
    for shape in DEFAULT_SHAPES:
        if shape["id"] == shape_id:
            return jsonify({
                "status": "success",
                "shape": shape
            })

    return jsonify({"status": "error", "message": "Shape not found"}), 404
