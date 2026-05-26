from flask import Blueprint, jsonify, request

canvas_ai_tools_bp = Blueprint("canvas_ai_tools_bp", __name__)

@canvas_ai_tools_bp.route("/ai/generate-background", methods=["POST"])
def generate_background():
    prompt = request.json.get("prompt", "abstract background")
    
    # Placeholder AI response
    return jsonify({
        "status": "success",
        "image_url": "https://via.placeholder.com/1200x800?text=AI+Background",
        "prompt_used": prompt
    })


@canvas_ai_tools_bp.route("/ai/remove-object", methods=["POST"])
def remove_object():
    image_url = request.json.get("image_url")
    
    return jsonify({
        "status": "success",
        "processed_image": "https://via.placeholder.com/1200x800?text=Object+Removed",
        "source": image_url
    })


@canvas_ai_tools_bp.route("/ai/auto-layout", methods=["POST"])
def auto_layout():
    elements = request.json.get("elements", [])
    
    # Fake auto-layout: center everything
    processed = []
    for el in elements:
        processed.append({
            **el,
            "x": 300,
            "y": 200
        })
    
    return jsonify({
        "status": "success",
        "elements": processed
    })
