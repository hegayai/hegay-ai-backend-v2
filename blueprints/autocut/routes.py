from flask import Blueprint, request, jsonify
import requests

autocut_bp = Blueprint("autocut_bp", __name__)

@autocut_bp.route("/cut", methods=["POST"])
def cut_video():
    data = request.get_json() or {}

    video_url = data.get("video_url", "")
    formats = data.get("formats", ["9:16", "1:1", "16:9"])
    durations = data.get("durations", [6, 15, 30])
    style = data.get("style", "default")  # default, cinematic, social

    if not video_url:
        return jsonify({"error": "video_url is required"}), 400

    # Call your video processing service (placeholder)
    r = requests.post(
        "http://localhost:5003/autocut",
        json={
            "video_url": video_url,
            "formats": formats,
            "durations": durations,
            "style": style
        }
    )

    res = r.json()

    return jsonify({
        "cuts": res.get("cuts", []),
        "formats": formats,
        "durations": durations,
        "style": style
    }), 200
