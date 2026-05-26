from flask import Blueprint, request, jsonify
import requests

voiceover_bp = Blueprint("voiceover_bp", __name__)

@voiceover_bp.route("/generate", methods=["POST"])
def generate_voiceover():
    data = request.get_json() or {}

    text = data.get("text", "")
    language = data.get("language", "English")
    voice_style = data.get("voice_style", "Neutral")
    format = data.get("format", "mp3")

    if not text:
        return jsonify({"error": "Text is required"}), 400

    # Call your TTS provider (placeholder)
    r = requests.post(
        "http://localhost:5001/tts",
        json={
            "text": text,
            "language": language,
            "voice_style": voice_style,
            "format": format
        }
    )

    res = r.json()

    return jsonify({
        "audio_url": res.get("audio_url"),
        "language": language,
        "voice_style": voice_style,
        "format": format
    }), 200
