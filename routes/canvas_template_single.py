from flask import Blueprint, jsonify

canvas_template_single = Blueprint("canvas_template_single", __name__)

@canvas_template_single.route("/template/<template_id>", methods=["GET"])
def get_template(template_id):
    templates = {
        "poster-1": {
            "elements": [
                {
                    "id": "title",
                    "type": "text",
                    "text": "BIG BOLD TITLE",
                    "fontSize": 48,
                    "color": "#ffffff",
                    "x": 200,
                    "y": 150,
                    "width": 600,
                    "height": 80
                },
                {
                    "id": "subtitle",
                    "type": "text",
                    "text": "Your subtitle goes here",
                    "fontSize": 24,
                    "color": "#cccccc",
                    "x": 200,
                    "y": 250,
                    "width": 600,
                    "height": 60
                },
                {
                    "id": "shape-bg",
                    "type": "shape",
                    "color": "#ffffff10",
                    "radius": 20,
                    "x": 150,
                    "y": 120,
                    "width": 700,
                    "height": 300
                }
            ]
        },

        "quote-1": {
            "elements": [
                {
                    "id": "quote",
                    "type": "text",
                    "text": "“Your quote here.”",
                    "fontSize": 36,
                    "color": "#ffffff",
                    "x": 180,
                    "y": 200,
                    "width": 500,
                    "height": 100
                }
            ]
        },

        "social-1": {
            "elements": [
                {
                    "id": "header",
                    "type": "text",
                    "text": "Instagram Promo",
                    "fontSize": 32,
                    "color": "#ffffff",
                    "x": 160,
                    "y": 120,
                    "width": 500,
                    "height": 80
                },
                {
                    "id": "shape-card",
                    "type": "shape",
                    "color": "#ffffff15",
                    "radius": 16,
                    "x": 140,
                    "y": 200,
                    "width": 540,
                    "height": 300
                }
            ]
        }
    }

    return jsonify(templates.get(template_id, {"elements": []}))
