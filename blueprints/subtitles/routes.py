from flask import Blueprint, request, jsonify
import requests

subtitles_bp = Blueprint("subtitles_bp", __name__)

@subtitles_bp.route("/generate", methods=["POST"])
def generate_subtitles():
    data = request.get_json() or {}

    video_url = data.get("video_url", "")
    language = data.get("language", "English")
    style = data.get("style", "default")  # default, social, cinematic

    if not video_url:
        return jsonify({"error": "video_url is required"}), 400

    # Call your STT/ASR + subtitle service (placeholder)
    r = requests.post(
        "http://localhost:5002/subtitles",
        json={
            "video_url": video_url,
            "language": language,
            "style": style
        }
    )

    res = r.json()

    return jsonify({
        "subtitle_url": res.get("subtitle_url"),
        "language": language,
        "style": style,
        "format": res.get("format", "srt")
    }), 200
