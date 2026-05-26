import requests
from utils.chat_memory import remember

def auto_cut_video(video_url: str, formats: list, durations: list, style: str, user_id: int):
    r = requests.post(
        "http://localhost:10000/autocut/cut",
        json={
            "video_url": video_url,
            "formats": formats,
            "durations": durations,
            "style": style
        }
    )

    res = r.json()

    cuts = res.get("cuts", [])

    remember(user_id, "last_autocuts", cuts)
    remember(user_id, "last_video", video_url)

    return {
        "cuts": cuts,
        "formats": formats,
        "durations": durations,
        "style": style
    }
