from flask import Blueprint, request, jsonify
from middleware.auth import require_auth
from utils.http import safe_json
from utils.logger import log_event

models_bp = Blueprint("models", __name__)

# -------------------------------------------------------------------
# Helper: Validate prompt
# -------------------------------------------------------------------
def require_prompt(data):
    prompt = data.get("prompt")
    if not prompt or not prompt.strip():
        return None, jsonify({"error": "Prompt is required"}), 400
    return prompt.strip(), None, None


# -------------------------------------------------------------------
# TEXT → IMAGE
# -------------------------------------------------------------------
@models_bp.post("/text_to_image")
@require_auth
def text_to_image():
    data = safe_json(request)
    prompt, err, code = require_prompt(data)
    if err:
        return err, code

    # Simulated output (replace with real model call)
    image_url = f"https://dummy.hegay.ai/generated/image/{hash(prompt)}.png"

    log_event("text_to_image", {"prompt": prompt})
    return jsonify({"image_url": image_url}), 200


# -------------------------------------------------------------------
# MOTION AI
# -------------------------------------------------------------------
@models_bp.post("/motion_ai")
@require_auth
def motion_ai():
    data = safe_json(request)
    prompt, err, code = require_prompt(data)
    if err:
        return err, code

    preview_url = f"https://dummy.hegay.ai/generated/motion/{hash(prompt)}.mp4"

    log_event("motion_ai", {"prompt": prompt})
    return jsonify({"preview_url": preview_url}), 200


# -------------------------------------------------------------------
# TEXT → VIDEO
# -------------------------------------------------------------------
@models_bp.post("/text_to_video")
@require_auth
def text_to_video():
    data = safe_json(request)
    prompt, err, code = require_prompt(data)
    if err:
        return err, code

    video_url = f"https://dummy.hegay.ai/generated/video/{hash(prompt)}.mp4"

    log_event("text_to_video", {"prompt": prompt})
    return jsonify({"video_url": video_url}), 200


# -------------------------------------------------------------------
# VIDEO UPSCALER
# -------------------------------------------------------------------
@models_bp.post("/video_upscaler")
@require_auth
def video_upscaler():
    data = safe_json(request)
    video_url = data.get("video_url")

    if not video_url:
        return jsonify({"error": "video_url is required"}), 400

    upscaled_url = f"{video_url}?upscaled=4k"

    log_event("video_upscaler", {"video_url": video_url})
    return jsonify({"video_url": upscaled_url}), 200


# -------------------------------------------------------------------
# MUSIC GENERATOR PRO
# -------------------------------------------------------------------
@models_bp.post("/music_generator_pro")
@require_auth
def music_generator_pro():
    data = safe_json(request)
    prompt, err, code = require_prompt(data)
    if err:
        return err, code

    audio_url = f"https://dummy.hegay.ai/generated/audio/{hash(prompt)}.mp3"

    log_event("music_generator_pro", {"prompt": prompt})
    return jsonify({"audio_url": audio_url}), 200


# -------------------------------------------------------------------
# AUDIO ENHANCER
# -------------------------------------------------------------------
@models_bp.post("/audio_enhancer")
@require_auth
def audio_enhancer():
    data = safe_json(request)
    audio_url = data.get("audio_url")

    if not audio_url:
        return jsonify({"error": "audio_url is required"}), 400

    enhanced_url = f"{audio_url}?enhanced=true"

    log_event("audio_enhancer", {"audio_url": audio_url})
    return jsonify({"audio_url": enhanced_url}), 200


# -------------------------------------------------------------------
# 3D MODEL GENERATOR
# -------------------------------------------------------------------
@models_bp.post("/3d_model_generator")
@require_auth
def model_3d():
    data = safe_json(request)
    prompt, err, code = require_prompt(data)
    if err:
        return err, code

    preview_url = f"https://dummy.hegay.ai/generated/3d/{hash(prompt)}.png"

    log_event("3d_model_generator", {"prompt": prompt})
    return jsonify({"preview_url": preview_url}), 200


# -------------------------------------------------------------------
# INTERIOR DESIGN (3D)
# -------------------------------------------------------------------
@models_bp.post("/interior_design_3d")
@require_auth
def interior_design():
    data = safe_json(request)
    prompt, err, code = require_prompt(data)
    if err:
        return err, code

    preview_url = f"https://dummy.hegay.ai/generated/interior/{hash(prompt)}.png"

    log_event("interior_design_3d", {"prompt": prompt})
    return jsonify({"preview_url": preview_url}), 200


# -------------------------------------------------------------------
# WORKER AGENT
# -------------------------------------------------------------------
@models_bp.post("/worker_agent")
@require_auth
def worker_agent():
    data = safe_json(request)
    task = data.get("task")

    if not task or not task.strip():
        return jsonify({"error": "task is required"}), 400

    log = [
        f"Worker Agent started task: {task}",
        "Analyzing requirements...",
        "Allocating GPU resources...",
        "Executing multi-step pipeline...",
        "Task completed successfully."
    ]

    log_event("worker_agent", {"task": task})
    return jsonify({"log": log}), 200


# -------------------------------------------------------------------
# HEGAY CHAT
# -------------------------------------------------------------------
@models_bp.post("/hegay_chat")
@require_auth
def hegay_chat():
    data = safe_json(request)
    messages = data.get("messages")

    if not messages or not isinstance(messages, list):
        return jsonify({"error": "messages must be an array"}), 400

    last = messages[-1]["content"]

    reply = f"I understand: {last}. How can I assist further?"

    log_event("hegay_chat", {"last_message": last})
    return jsonify({"reply": reply}), 200
