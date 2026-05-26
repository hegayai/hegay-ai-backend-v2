import random
from utils.brand_style_memory import get_brand_style
from utils.admin_workflow_templates import get_admin_template
from utils.workflow_engine import execute_task
from utils.chat_memory import remember

# ---------------------------------------------------------
# ⭐ PROMOTION IDEA GENERATOR
# ---------------------------------------------------------
PROMO_IDEA_BANK = [
    "Introducing the new Motion Engine",
    "Create anything with Hegay AI Studio",
    "Global creators using Hegay AI",
    "New cinematic workflow update",
    "Brand advertisement automation",
    "AI-powered social media content",
    "Hegay AI for businesses worldwide",
    "Premium creative OS for everyone",
    "Next-gen video generation",
    "Hegay AI: Create without limits"
]

def generate_promo_ideas(count=5):
    return random.sample(PROMO_IDEA_BANK, count)


# ---------------------------------------------------------
# ⭐ BUILD PROMOTION WORKFLOW FROM TEMPLATE
# ---------------------------------------------------------
def build_promo_workflow(template_name, headline, subtext, user_id):
    brand = get_brand_style(user_id, "Hegay AI")

    if not brand:
        # Default fallback
        brand_data = {
            "brand_name": "Hegay AI",
            "primary_color": "#0A84FF",
            "secondary_color": "#1C1C1E",
            "accent_color": "#FFFFFF",
            "font_family": "SF Pro Display",
            "design_language": "Futuristic OS UI",
            "tone": "Premium, global, cinematic"
        }
    else:
        brand_data = {
            "brand_name": brand.brand_name,
            "primary_color": brand.primary_color,
            "secondary_color": brand.secondary_color,
            "accent_color": brand.accent_color,
            "font_family": brand.font_family,
            "design_language": brand.design_language,
            "tone": brand.tone
        }

    template = get_admin_template(template_name)
    if not template:
        return None

    steps = []

    for step in template["steps"]:
        if step["type"] == "image":
            steps.append({
                "type": "image",
                "prompt": step["prompt_template"].format(
                    headline=headline,
                    subtext=subtext,
                    **brand_data
                ),
                "language": "English"
            })

        elif step["type"] == "video":
            steps.append({
                "type": "video",
                "prompt": step["prompt_template"].format(
                    headline=headline,
                    subtext=subtext,
                    **brand_data
                ),
                "duration": step.get("duration", 10),
                "language": "English"
            })

    return steps


# ---------------------------------------------------------
# ⭐ EXECUTE PROMOTION WORKFLOW
# ---------------------------------------------------------
def run_promo_workflow(steps, cookies, project_id, user_id):
    results = []

    for step in steps:
        result = execute_task(step, cookies, project_id, user_id)
        results.append(result)

    remember(user_id, "last_promo", results)
    return results
