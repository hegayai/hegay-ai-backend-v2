from flask import Blueprint, request, jsonify
from utils.promotion_engine import generate_promo_ideas, build_promo_workflow, run_promo_workflow
from models.project import Project
from database import db
from utils.chat_memory import remember, recall

promotion_bp = Blueprint("promotion_bp", __name__)

# ---------------------------------------------------------
# ⭐ GET PROMO IDEAS (ADMIN)
# ---------------------------------------------------------
@promotion_bp.route("/admin/promo/ideas", methods=["GET"])
def admin_promo_ideas():
    user_id = 1  # TODO: real session user
    ideas = generate_promo_ideas(5)
    remember(user_id, "last_promo_ideas", ideas)
    return jsonify({"ideas": ideas}), 200


# ---------------------------------------------------------
# ⭐ RUN PROMO WORKFLOW (ADMIN)
# ---------------------------------------------------------
@promotion_bp.route("/admin/promo/run", methods=["POST"])
def admin_promo_run():
    data = request.get_json() or {}
    user_id = 1

    template_name = data.get("template_name", "promo_image")
    headline = data.get("headline", "Introducing Hegay AI")
    subtext = data.get("subtext", "The global creative OS for brands and creators.")

    # Ensure project exists
    project_id = recall(user_id, "last_promo_project")
    if not project_id:
        p = Project(user_id=user_id, name="Hegay Promo Campaigns")
        db.session.add(p)
        db.session.commit()
        project_id = p.id
        remember(user_id, "last_promo_project", str(project_id))

    steps = build_promo_workflow(template_name, headline, subtext, user_id)
    if not steps:
        return jsonify({"error": "Invalid template name"}), 400

    results = run_promo_workflow(steps, request.cookies, project_id, user_id)

    return jsonify({
        "template_name": template_name,
        "headline": headline,
        "subtext": subtext,
        "project_id": project_id,
        "results": results
    }), 200
