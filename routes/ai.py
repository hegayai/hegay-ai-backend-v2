from flask import Blueprint, request, jsonify, session
from models.user import User
from models.system_config import FeatureFlag, PlanConfig, ResolutionConfig
from models.billing import BillingEvent
from utils.allowances import get_plan_allowances
from utils.video_limits import get_max_video_seconds
from utils.credits import calculate_credit_usage
from pricing.credits import (
    credits_for_music_video,
    MOTION_CREDITS_PER_SECOND,
    REELS_CREDITS_PER_SECOND,
    BRANDING_SUITE_CREDITS,
    WORKER_AGENT_CREDITS,
    MUSIC_CREATION_CREDITS,
    MUSIC_VIDEO_CREDITS,
    SUBTITLE_CREDITS_PER_MINUTE,
)
from models import db

ai_bp = Blueprint("ai", __name__)

# -----------------------------
# BILLING HELPERS (PUT THEM HERE)
# -----------------------------
def deduct_credits(user: User, credits: int, feature: str, details: dict):
    user.credits_used = (user.credits_used or 0) + credits
    user.credits_remaining = (user.credits_remaining or 0) - credits

    event = BillingEvent(
        user_id=user.id,
        plan=user.plan,
        category="B",
        feature=feature,
        credits_used=credits,
        details=details,
    )

    db.session.add(event)
    db.session.commit()


def log_plan_usage(user: User, feature: str, details: dict):
    event = BillingEvent(
        user_id=user.id,
        plan=user.plan,
        category="A",
        feature=feature,
        credits_used=0,
        details=details,
    )
    db.session.add(event)
    db.session.commit()


# -----------------------------
# HELPERS
# -----------------------------
def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)


def is_feature_enabled(name: str) -> bool:
    flag = FeatureFlag.query.filter_by(name=name).first()
    return bool(flag and flag.enabled)


def is_plan_active(plan_name: str) -> bool:
    plan = PlanConfig.query.filter_by(name=plan_name).first()
    return bool(plan and plan.is_active)


def get_resolution_multiplier(resolution: str):
    res = ResolutionConfig.query.filter_by(name=resolution).first()
    if not res or not res.is_active:
        return None
    return res.multiplier


def is_category_a(plan: str) -> bool:
    return plan in ["Free", "Starter", "Creator", "Pro", "Studio"]


def deduct_credits(user: User, credits: int, feature: str, metadata: dict):
    user.credits_used = (user.credits_used or 0) + credits
    user.credits_remaining = (user.credits_remaining or 0) - credits

    event = BillingEvent(
        user_id=user.id,
        plan=user.plan,
        category="B",
        feature=feature,
        credits_used=credits,
        metadata=metadata,
    )

    db.session.add(event)
    db.session.commit()


def log_plan_usage(user: User, feature: str, metadata: dict):
    event = BillingEvent(
        user_id=user.id,
        plan=user.plan,
        category="A",
        feature=feature,
        credits_used=0,
        metadata=metadata,
    )
    db.session.add(event)
    db.session.commit()


# -----------------------------
# CHAT
# -----------------------------
@ai_bp.route("/chat", methods=["POST"])
def chat():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.get_json()
    prompt = data.get("prompt")

    if user.role != "admin" and not is_feature_enabled("chat_enabled"):
        return jsonify({"error": "Chat is currently disabled"}), 403

    # Optional: log chat usage later if needed
    return jsonify({"reply": f"AI response to: {prompt}"})


# -----------------------------
# IMAGE GENERATION
# -----------------------------
@ai_bp.route("/image", methods=["POST"])
def image():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401

    if user.role != "admin":
        if not is_feature_enabled("image_generation"):
            return jsonify({"error": "Image generation is currently disabled"}), 403

        if is_category_a(user.plan) and not is_plan_active(user.plan):
            return jsonify({"error": "Your plan is currently unavailable"}), 403

    allowances = get_plan_allowances(user.plan)

    if is_category_a(user.plan):
        if user.images_generated >= allowances["images"]:
            return jsonify({"error": "Image limit reached"}), 403

        user.images_generated = (user.images_generated or 0) + 1
        db.session.commit()

        log_plan_usage(user, "image", {"type": "image_generation"})
    else:
        credits_needed = calculate_credit_usage("image")
        if user.credits_remaining < credits_needed:
            return jsonify({"error": "Not enough credits"}), 403

        deduct_credits(user, credits_needed, "image", {"type": "image_generation"})

    return jsonify({"message": "Image generation endpoint coming soon"})


# -----------------------------
# AUDIO GENERATION
# -----------------------------
@ai_bp.route("/audio", methods=["POST"])
def audio():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401

    if user.role != "admin" and not is_feature_enabled("audio_generation"):
        return jsonify({"error": "Audio generation is currently disabled"}), 403

    # If you later make audio Category B, add credit deduction + BillingEvent here
    return jsonify({"message": "Audio generation endpoint coming soon"})


# -----------------------------
# VIDEO GENERATION
# -----------------------------
@ai_bp.route("/video", methods=["POST"])
def video():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.get_json()
    requested_seconds = int(data.get("seconds", 5))
    resolution = data.get("resolution", "720p")

    if user.role == "admin":
        return jsonify({"message": "Admin video generation endpoint coming soon"})

    if not is_feature_enabled("video_generation"):
        return jsonify({"error": "Video generation is currently disabled"}), 403

    res_multiplier = get_resolution_multiplier(resolution)
    if res_multiplier is None:
        return jsonify({"error": f"{resolution} is not available yet"}), 403

    max_seconds = get_max_video_seconds(user)
    if requested_seconds > max_seconds:
        return jsonify({"error": "Video duration exceeds your plan limit"}), 403

    allowances = get_plan_allowances(user.plan)

    if is_category_a(user.plan):
        if not is_plan_active(user.plan):
            return jsonify({"error": "Your plan is currently unavailable"}), 403

        if user.videos_generated >= allowances["videos"]:
            return jsonify({"error": "Video limit reached"}), 403

        user.videos_generated = (user.videos_generated or 0) + 1
        db.session.commit()

        log_plan_usage(
            user,
            "video",
            {"seconds": requested_seconds, "resolution": resolution},
        )
    else:
        credits_needed = calculate_credit_usage(
            "video",
            seconds=requested_seconds,
            resolution=resolution,
        )
        if user.credits_remaining < credits_needed:
            return jsonify({"error": "Not enough credits"}), 403

        deduct_credits(
            user,
            credits_needed,
            "video",
            {"seconds": requested_seconds, "resolution": resolution},
        )

    return jsonify({"message": "Video generation endpoint coming soon"})


# -----------------------------
# MUSIC VIDEO GENERATOR
# -----------------------------
@ai_bp.route("/music-video", methods=["POST"])
def music_video():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.get_json()
    requested_seconds = int(data.get("seconds", 8))
    resolution = data.get("resolution", "720p")

    if user.role == "admin":
        return jsonify({"message": "Admin music video generation endpoint coming soon"})

    if not is_feature_enabled("music_video"):
        return jsonify({"error": "Music video generator is not yet released"}), 403

    res_multiplier = get_resolution_multiplier(resolution)
    if res_multiplier is None:
        return jsonify({"error": f"{resolution} is not available yet"}), 403

    max_seconds = get_max_video_seconds(user)
    if requested_seconds > max_seconds:
        return jsonify({"error": "Music video duration exceeds your plan limit"}), 403

    credits_needed = credits_for_music_video(requested_seconds, resolution)
    if user.credits_remaining < credits_needed:
        return jsonify({"error": "Not enough credits"}), 403

    deduct_credits(
        user,
        credits_needed,
        "music_video",
        {"seconds": requested_seconds, "resolution": resolution},
    )

    return jsonify({"message": "Music video generation endpoint coming soon"})


# -----------------------------
# CANVAS AI
# -----------------------------
@ai_bp.route("/canvas", methods=["POST"])
def canvas():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401

    if user.role != "admin" and not is_feature_enabled("canvas_ai"):
        return jsonify({"error": "Canvas AI is currently disabled"}), 403

    allowances = get_plan_allowances(user.plan)

    if is_category_a(user.plan):
        if not is_plan_active(user.plan):
            return jsonify({"error": "Your plan is currently unavailable"}), 403

        if user.canvas_actions >= allowances["canvas_limit"]:
            return jsonify({"error": "Canvas limit reached"}), 403

        user.canvas_actions = (user.canvas_actions or 0) + 1
        db.session.commit()

        log_plan_usage(user, "canvas", {"type": "canvas_action"})
    else:
        credits_needed = calculate_credit_usage("canvas")
        if user.credits_remaining < credits_needed:
            return jsonify({"error": "Not enough credits"}), 403

        deduct_credits(user, credits_needed, "canvas", {"type": "canvas_action"})

    return jsonify({"message": "Canvas AI endpoint coming soon"})


# -----------------------------
# MOTION AI
# -----------------------------
@ai_bp.route("/motion", methods=["POST"])
def motion():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.get_json()
    requested_seconds = int(data.get("seconds", 8))

    if user.role == "admin":
        return jsonify({"message": "Admin motion endpoint coming soon"})

    if not is_feature_enabled("motion_ai"):
        return jsonify({"error": "Motion AI is not yet released"}), 403

    max_seconds = get_max_video_seconds(user)
    if requested_seconds > max_seconds:
        return jsonify({"error": "Motion duration exceeds your plan limit"}), 403

    credits_needed = requested_seconds * MOTION_CREDITS_PER_SECOND
    if user.credits_remaining < credits_needed:
        return jsonify({"error": "Not enough credits"}), 403

    deduct_credits(
        user,
        credits_needed,
        "motion",
        {"seconds": requested_seconds},
    )

    return jsonify({"message": "Motion AI endpoint coming soon"})


# -----------------------------
# REELS ENGINE
# -----------------------------
@ai_bp.route("/reels", methods=["POST"])
def reels():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.get_json()
    requested_seconds = int(data.get("seconds", 10))

    if user.role == "admin":
        return jsonify({"message": "Admin reels endpoint coming soon"})

    if not is_feature_enabled("reels_engine"):
        return jsonify({"error": "Reels engine is not yet released"}), 403

    max_seconds = get_max_video_seconds(user)
    if requested_seconds > max_seconds:
        return jsonify({"error": "Reels duration exceeds your plan limit"}), 403

    credits_needed = requested_seconds * REELS_CREDITS_PER_SECOND
    if user.credits_remaining < credits_needed:
        return jsonify({"error": "Not enough credits"}), 403

    deduct_credits(
        user,
        credits_needed,
        "reels",
        {"seconds": requested_seconds},
    )

    return jsonify({"message": "Reels engine endpoint coming soon"})


# -----------------------------
# WORKER AGENT
# -----------------------------
@ai_bp.route("/worker-agent", methods=["POST"])
def worker_agent():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401

    if user.role == "admin":
        return jsonify({"message": "Admin worker agent endpoint coming soon"})

    if not is_feature_enabled("worker_agent"):
        return jsonify({"error": "Worker Agent is not yet released"}), 403

    credits_needed = WORKER_AGENT_CREDITS
    if user.credits_remaining < credits_needed:
        return jsonify({"error": "Not enough credits"}), 403

    deduct_credits(
        user,
        credits_needed,
        "worker_agent",
        {"type": "worker_task"},
    )

    return jsonify({"message": "Worker Agent endpoint coming soon"})


# -----------------------------
# MUSIC CREATION
# -----------------------------
@ai_bp.route("/music", methods=["POST"])
def music():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401

    if user.role == "admin":
        return jsonify({"message": "Admin music endpoint coming soon"})

    if not is_feature_enabled("music_creation"):
        return jsonify({"error": "Music creation is not yet released"}), 403

    credits_needed = MUSIC_CREATION_CREDITS
    if user.credits_remaining < credits_needed:
        return jsonify({"error": "Not enough credits"}), 403

    deduct_credits(
        user,
        credits_needed,
        "music",
        {"type": "music_creation"},
    )

    return jsonify({"message": "Music creation endpoint coming soon"})


# -----------------------------
# SUBTITLE ENGINE
# -----------------------------
@ai_bp.route("/subtitles", methods=["POST"])
def subtitles():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.get_json()
    minutes = float(data.get("minutes", 1))

    if user.role == "admin":
        return jsonify({"message": "Admin subtitles endpoint coming soon"})

    if not is_feature_enabled("subtitle_engine"):
        return jsonify({"error": "Subtitle engine is not yet released"}), 403

    credits_needed = int(minutes * SUBTITLE_CREDITS_PER_MINUTE)
    if user.credits_remaining < credits_needed:
        return jsonify({"error": "Not enough credits"}), 403

    deduct_credits(
        user,
        credits_needed,
        "subtitles",
        {"minutes": minutes},
    )

    return jsonify({"message": "Subtitle engine endpoint coming soon"})
