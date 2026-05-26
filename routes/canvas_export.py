from flask import Blueprint, jsonify, request

canvas_export_bp = Blueprint("canvas_export_bp", __name__)

@canvas_export_bp.route("/export/json", methods=["POST"])
def export_json():
    elements = request.json.get("elements", [])

    return jsonify({
        "status": "success",
        "export_type": "json",
        "data": elements
    })


@canvas_export_bp.route("/export/image", methods=["POST"])
def export_image():
    elements = request.json.get("elements", [])

    # Placeholder export image URL
    return jsonify({
        "status": "success",
        "export_type": "image",
        "image_url": "https://via.placeholder.com/1200x800?text=Canvas+Export",
        "elements_received": len(elements)
    })


@canvas_export_bp.route("/export/project", methods=["POST"])
def export_project():
    elements = request.json.get("elements", [])
    metadata = request.json.get("metadata", {})

    return jsonify({
        "status": "success",
        "export_type": "project",
        "project": {
            "elements": elements,
            "metadata": metadata
        }
    })
