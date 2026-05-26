from flask import Blueprint, request, jsonify
from utils.workflow_engine import detect_tasks, execute_task
from utils.workflow_templates import get_template
from utils.chat_memory import remember, recall, recall_all
from models.project import Project
from database import db

chat_bp = Blueprint("chat_bp", __name__)

# ---------------------------------------------------------
# ⭐ FILL TEMPLATE FIELDS
# ---------------------------------------------------------
def fill_template(template_str: str, variables: dict):
    try:
        return template_str.format(**variables)
    except KeyError:
        return template_str


# ---------------------------------------------------------
# ⭐ APPLY WORKFLOW TEMPLATE
# ---------------------------------------------------------
def apply_template(template_name: str, message: str, user_id: int):
    template = get_template(template_name)
    if not template:
        return None

    # Extract variables from message (simple version)
    variables = {
        "subject": message,
        "player_name": message,
        "team_colors": "team colors",
        "movement_type": "dynamic movement",
        "energy_level": "high",
        "style": "global cinematic",
        "theme": "universal theme",
        "dance_style": "global dance",
        "vibe": "energetic",
        "brand_name": "Global Brand",
        "product_name": "Product",
        "visual_style": "premium global style",
        "color_palette": "brand colors",
        "design_language": "modern global design",
        "selling_point": "key selling point",
        "tone": "professional",
        "brand_motion_style": "smooth global motion",
        "target_audience": "global audience",
    }

    steps = []

    for step in template["steps"]:
        if step["type"] == "image":
            steps.append({
                "type": "image",
                "prompt": fill_template(step["prompt_template"], variables)
            })

        elif step["type"] == "motion":
            steps.append({
                "type": "motion",
                "reference": fill_template(step["reference_template"], variables)
            })

        elif step["type"] == "video":
            steps.append({
                "type": "video",
                "prompt": fill_template(step["prompt_template"], variables),
                "duration": step.get("duration", 5)
            })

    return steps


# ---------------------------------------------------------
# ⭐ MAIN WORKFLOW ROUTE
# ---------------------------------------------------------
@chat_bp.route("/workflow", methods=["POST"])
def workflow():
    data = request.get_json() or {}
    message = data.get("message", "").strip()
    user_id = 1  # TODO: replace with real session user

    # ⭐ Detect if user wants a template workflow
    template_name = None
    msg = message.lower()

    if "cinematic" in msg:
        template_name = "cinematic"
    elif "football" in msg:
        template_name = "football"
    elif "dance" in msg:
        template_name = "dance"
    elif "brand" in msg or "advert" in msg or "promotion" in msg:
        template_name = "branding"

    # ⭐ If template exists → use template workflow
    if template_name:
        tasks = apply_template(template_name, message, user_id)
    else:
        # ⭐ Otherwise → use normal task detection
        tasks = detect_tasks(message)

    if not tasks:
        return jsonify({
            "type": "chat",
            "response": "I understand your message, but I don't see any creative tasks to execute.",
            "memory": recall_all(user_id)
        }), 200

    # ⭐ Ensure project exists
    project_id = recall(user_id, "last_project")
    if not project_id:
        p = Project(user_id=user_id, name="Untitled Project")
        db.session.add(p)
        db.session.commit()
        remember(user_id, "last_project", str(p.id))
        project_id = p.id

    results = []

    # ⭐ Execute tasks in order
    for task in tasks:
        result = execute_task(task, request.cookies, project_id, user_id)
        results.append(result)

    # ⭐ Return workflow summary
    return jsonify({
        "type": "workflow",
        "workflow_template": template_name,
        "project_id": project_id,
        "tasks_executed": len(tasks),
        "results": results,
        "memory": recall_all(user_id)
    }), 200
