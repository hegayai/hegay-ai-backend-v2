from flask import Blueprint, request, jsonify
from utils.allowances import get_plan_allowances
from utils.credits import calculate_credit_usage
from utils.video_limits import get_max_video_seconds
from models.user import User
from flask import session

ai_bp = Blueprint("ai", __name__)

# -----------------------------
# CHAT
# -----------------------------
@ai_bp.route("/chat", methods=["POST"])
def chat():
    user_id = session.get("user_id")
    user = User.query.get(user_id)

    data = request.get_json()
    prompt = data.get("prompt")

    return jsonify({"reply": f"AI response to: {prompt}"})


# -----------------------------
# IMAGE GENERATION
# -----------------------------
@ai_bp.route("/image", methods=["POST"])
def image():
    user_id = session.get("user_id")
    user = User.query.get(user_id)

    allowances = get_plan_allowances(user.plan)

    # CATEGORY A (subscription)
    if user.plan in ["Free", "Starter", "Creator", "Pro", "Studio"]:
        if user.images_generated >= allowances["images"]:
            return jsonify({"error": "Image limit reached"}), 403

    # CATEGORY B (credits)
    else:
        credits_needed = calculate_credit_usage("image")
        if user.credits_remaining < credits_needed:
            return jsonify({"error": "Not enough credits"}), 403

    return jsonify({"message": "Image generation endpoint coming soon"})


# -----------------------------
# AUDIO GENERATION
# -----------------------------
@ai_bp.route("/audio", methods=["POST"])
def audio():
    user_id = session.get("user_id")
    user = User.query.get(user_id)

    return jsonify({"message": "Audio generation endpoint coming soon"})


# -----------------------------
# VIDEO GENERATION
# -----------------------------
@ai_bp.route("/video", methods=["POST"])
def video():
    user_id = session.get("user_id")
    user = User.query.get(user_id)

    data = request.get_json()
    requested_seconds = int(data.get("seconds", 5))
    resolution = data.get("resolution", "720p")

    max_seconds = get_max_video_seconds(user)

    if requested_seconds > max_seconds:
        return jsonify({"error": "Video duration exceeds plan limit"}), 403

    allowances = get_plan_allowances(user.plan)

    # CATEGORY A (subscription)
    if user.plan in ["Free", "Starter", "Creator", "Pro", "Studio"]:
        if user.videos_generated >= allowances["videos"]:
            return jsonify({"error": "Video limit reached"}), 403

    # CATEGORY B (credits)
    else:
        credits_needed = calculate_credit_usage(
            "video",
            seconds=requested_seconds,
            resolution=resolution
        )
        if user.credits_remaining < credits_needed:
            return jsonify({"error": "Not enough credits"}), 403

    return jsonify({"message": "Video generation endpoint coming soon"})


# -----------------------------
# CANVAS AI
# -----------------------------
@ai_bp.route("/canvas", methods=["POST"])
def canvas():
    user_id = session.get("user_id")
    user = User.query.get(user_id)

    allowances = get_plan_allowances(user.plan)

    # CATEGORY A
    if user.plan in ["Free", "Starter", "Creator", "Pro", "Studio"]:
        if user.canvas_actions >= allowances["canvas_limit"]:
            return jsonify({"error": "Canvas limit reached"}), 403

    # CATEGORY B
    else:
        credits_needed = calculate_credit_usage("canvas")
        if user.credits_remaining < credits_needed:
            return jsonify({"error": "Not enough credits"}), 403

    return jsonify({"message": "Canvas AI endpoint coming soon"})
