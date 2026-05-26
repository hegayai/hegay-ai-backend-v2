import requests
from utils.chat_memory import remember

def generate_voiceover(text, language, voice_style, format, user_id):
    r = requests.post(
        "http://localhost:10000/voiceover/generate",
        json={
            "text": text,
            "language": language,
            "voice_style": voice_style,
            "format": format
        }
    )

    res = r.json()

    remember(user_id, "last_voiceover", res.get("audio_url"))
    remember(user_id, "last_language", language)

    return res.get("audio_url")
