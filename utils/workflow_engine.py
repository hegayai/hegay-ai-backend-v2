from utils.chat_memory import remember
from models.project_asset import ProjectAsset
from database import db
import requests

# ---------------------------------------------------------
# ⭐ SIMPLE LANGUAGE DETECTION (PLACEHOLDER)
# ---------------------------------------------------------
def detect_language(message: str) -> str:
    msg = message.lower()

    # Very simple heuristic — you can later replace with real detection
    if any(w in msg for w in ["hola", "gracias", "buenos", "día", "tarde"]):
        return "Spanish"
    if any(w in msg for w in ["olá", "obrigado", "obrigada", "bom dia"]):
        return "Portuguese"
    if any(w in msg for w in ["hallo", "danke", "guten tag", "guten morgen"]):
        return "German"
    if any(w in msg for w in ["bonjour", "merci", "salut"]):
        return "French"
    if any(w in msg for w in ["ciao", "grazie", "buongiorno"]):
        return "Italian"
    if any(w in msg for w in ["yoruba", "naija", "lagos", "abuja"]):
        return "Yoruba"
    # Default
    return "English"


# ---------------------------------------------------------
# ⭐ DETECT TASKS FROM USER MESSAGE (LANGUAGE‑AWARE)
# ---------------------------------------------------------
def detect_tasks(message: str):
    msg = message.lower()
    language = detect_language(message)
    tasks = []

    # IMAGE TASK
    if any(k in msg for k in ["image", "picture", "portrait", "photo", "draw", "imagen", "foto", "bild"]):
        tasks.append({
            "type": "image",
            "prompt": message,
            "language": language,
        })

    # VIDEO TASK
    if any(k in msg for k in ["video", "clip", "film", "cinematic", "intro", "vídeo", "video clip"]):
        tasks.append({
            "type": "video",
            "prompt": message,
            "duration": 5,
            "language": language,
        })

    # MOTION TASK
    if any(k in msg for k in ["motion", "dance", "act", "reference video", "movement", "danza", "tanz"]):
        tasks.append({
            "type": "motion",
            "reference": message,
            "language": language,
        })

    return tasks


# ---------------------------------------------------------
# ⭐ EXECUTE A SINGLE WORKFLOW TASK (LANGUAGE‑AWARE)
# ---------------------------------------------------------
def execute_task(task, cookies, project_id, user_id):
    language = task.get("language", "English")

    # Helper: prefix prompt with language hint for the model
    def lang_prompt(base: str) -> str:
        return f"[Language: {language}] {base}"

    # -----------------------------------------------------
    # IMAGE GENERATION
    # -----------------------------------------------------
    if task["type"] == "image":
        r = requests.post(
            "http://localhost:10000/studio/image/generate",
            json={"prompt": lang_prompt(task["prompt"])},
            cookies=cookies
        )
        res = r.json()

        asset = ProjectAsset(
            project_id=project_id,
            type="image",
            url=res.get("image_url"),
            metadata=res
        )
        db.session.add(asset)
        db.session.commit()

        remember(user_id, "last_asset", res.get("image_url"))
        remember(user_id, "last_engine", "image")
        remember(user_id, "last_language", language)

        return {
            "status": "ok",
            "type": "image",
            "asset": res.get("image_url"),
            "language": language,
        }

    # -----------------------------------------------------
    # VIDEO GENERATION
    # -----------------------------------------------------
    if task["type"] == "video":
        r = requests.post(
            "http://localhost:10000/studio/video/generate",
            json={
                "prompt": lang_prompt(task["prompt"]),
                "duration": task.get("duration", 5),
            },
            cookies=cookies
        )
        res = r.json()

        asset = ProjectAsset(
            project_id=project_id,
            type="video",
            url=res.get("video_url"),
            metadata=res
        )
        db.session.add(asset)
        db.session.commit()

        remember(user_id, "last_asset", res.get("video_url"))
        remember(user_id, "last_engine", "video")
        remember(user_id, "last_language", language)

        return {
            "status": "ok",
            "type": "video",
            "asset": res.get("video_url"),
            "language": language,
        }

    # -----------------------------------------------------
    # MOTION TRANSFER (ADMIN)
    # -----------------------------------------------------
    if task["type"] == "motion":
        r = requests.post(
            "http://localhost:10000/studio/motion/apply",
            json={"reference_description": lang_prompt(task["reference"])},
            cookies=cookies
        )
        res = r.json()

        asset = ProjectAsset(
            project_id=project_id,
            type="motion",
            url=res.get("video_url"),
            metadata=res
        )
        db.session.add(asset)
        db.session.commit()

        remember(user_id, "last_asset", res.get("video_url"))
        remember(user_id, "last_engine", "motion")
        remember(user_id, "last_language", language)

        return {
            "status": "ok",
            "type": "motion",
            "asset": res.get("video_url"),
            "language": language,
        }

    # -----------------------------------------------------
    # UNKNOWN TASK TYPE
    # -----------------------------------------------------
    return {
        "status": "unknown",
        "type": task.get("type", "unknown"),
        "asset": None,
        "language": language,
    }
