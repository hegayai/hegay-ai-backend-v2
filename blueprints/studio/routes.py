from flask import Blueprint, request, jsonify
from database import db
from models.engine import Engine

studio_bp = Blueprint("studio_bp", __name__)

# ---------------------------------------------------------
# ⭐ HELPERS
# ---------------------------------------------------------
def _get_engine(name: str) -> Engine | None:
    return Engine.query.filter_by(name=name).first()


def _ensure_engine_running(name: str):
    engine = _get_engine(name)
    if not engine:
        return None, jsonify({"error": f"{name} engine not found"}), 404
    if engine.status != "running":
        return None, jsonify({"error": f"{name} engine is not running"}), 503
    return engine, None, None


# ---------------------------------------------------------
# ⭐ IMAGE FORGE → IMAGE ENGINE
# ---------------------------------------------------------
@studio_bp.route("/image/generate", methods=["POST"])
def generate_image():
    engine, err_resp, code = _ensure_engine_running("image")
    if err_resp:
        return err_resp, code

    data = request.get_json() or {}
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    # TODO: Replace this with real image generation call
    fake_url = f"https://dummy.hegay.local/image/{engine.current_model}/{engine.version}"

    # Simulate queue usage
    engine.queue_length = max(engine.queue_length - 1, 0)
    db.session.commit()

    return jsonify({
        "engine": engine.name,
        "model": engine.current_model,
        "version": engine.version,
        "prompt": prompt,
        "image_url": fake_url,
    }), 200


# ---------------------------------------------------------
# ⭐ VIDEO LAB → VIDEO ENGINE
# ---------------------------------------------------------
@studio_bp.route("/video/generate", methods=["POST"])
def generate_video():
    engine, err_resp, code = _ensure_engine_running("video")
    if err_resp:
        return err_resp, code

    data = request.get_json() or {}
    prompt = data.get("prompt", "").strip()
    duration = int(data.get("duration", 5))

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    # TODO: Replace this with real video generation call
    fake_url = f"https://dummy.hegay.local/video/{engine.current_model}/{engine.version}/{duration}s"

    engine.queue_length = max(engine.queue_length - 1, 0)
    db.session.commit()

    return jsonify({
        "engine": engine.name,
        "model": engine.current_model,
        "version": engine.version,
        "prompt": prompt,
        "duration": duration,
        "video_url": fake_url,
    }), 200


# ---------------------------------------------------------
# ⭐ MOTION LAB (ADMIN‑ONLY) → MOTION ENGINE (STUB)
# ---------------------------------------------------------
@studio_bp.route("/motion/apply", methods=["POST"])
def apply_motion():
    engine, err_resp, code = _ensure_engine_running("motion")
    if err_resp:
        return err_resp, code

    # NOTE: This is a stub for now — real implementation will:
    # - accept image + reference video
    # - run motion transfer
    # - return generated video
    data = request.get_json() or {}
    ref_desc = data.get("reference_description", "reference motion")

    fake_url = f"https://dummy.hegay.local/motion/{engine.current_model}/{engine.version}"

    engine.queue_length = max(engine.queue_length - 1, 0)
    db.session.commit()

    return jsonify({
        "engine": engine.name,
        "model": engine.current_model,
        "version": engine.version,
        "reference": ref_desc,
        "video_url": fake_url,
        "note": "Motion engine stub — full motion transfer pipeline to be wired here.",
    }), 200
