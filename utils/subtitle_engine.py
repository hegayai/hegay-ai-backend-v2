import requests
from utils.chat_memory import remember

def generate_subtitles_for_video(video_url: str, language: str, style: str, user_id: int):
    r = requests.post(
        "http://localhost:10000/subtitles/generate",
        json={
            "video_url": video_url,
            "language": language,
            "style": style
        }
    )

    res = r.json()

    subtitle_url = res.get("subtitle_url")

    remember(user_id, "last_subtitles", subtitle_url)
    remember(user_id, "last_language", language)

    return {
        "subtitle_url": subtitle_url,
        "language": language,
        "style": style,
        "format": res.get("format", "srt")
    }
