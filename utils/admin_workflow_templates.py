# ---------------------------------------------------------
# ⭐ HEGAY ADMIN BRAND-AWARE WORKFLOW TEMPLATES
#    (For Hegay AI self-promotion)
# ---------------------------------------------------------

ADMIN_BRAND_WORKFLOW_TEMPLATES = {
    # -----------------------------------------------------
    # ⭐ PROMO IMAGE (SOCIAL / LANDING)
    # -----------------------------------------------------
    "promo_image": {
        "name": "Hegay Promo Image",
        "description": "Generates a premium promotional image for Hegay AI features or campaigns.",
        "steps": [
            {
                "type": "image",
                "prompt_template": (
                    "Create a premium promotional image for Hegay AI with the headline: \"{headline}\". "
                    "Use Hegay brand colors: {primary_color}, {secondary_color}, {accent_color}. "
                    "Design language: {design_language}. "
                    "Include subtle futuristic UI elements and keep it clean, cinematic, and global."
                )
            }
        ]
    },

    # -----------------------------------------------------
    # ⭐ PROMO VIDEO (FEATURE / PRODUCT)
    # -----------------------------------------------------
    "promo_video": {
        "name": "Hegay Promo Video",
        "description": "Generates a short promotional video for Hegay AI features or launches.",
        "steps": [
            {
                "type": "video",
                "prompt_template": (
                    "Generate a cinematic promotional video for Hegay AI about: \"{headline}\". "
                    "Visual style: {visual_style}. "
                    "Use Hegay brand colors: {primary_color}, {secondary_color}, {accent_color}. "
                    "Tone: {tone}. "
                    "Show abstract AI visuals, creative workflows, and global creators using Hegay."
                ),
                "duration": 12
            }
        ]
    },

    # -----------------------------------------------------
    # ⭐ SOCIAL MEDIA PACK (IMAGES + VIDEO)
    # -----------------------------------------------------
    "social_pack": {
        "name": "Hegay Social Media Pack",
        "description": "Generates a set of assets for social media promotion.",
        "steps": [
            {
                "type": "image",
                "prompt_template": (
                    "Create a square social media promo image for Hegay AI with the text: \"{headline}\". "
                    "Use Hegay brand colors: {primary_color}, {secondary_color}, {accent_color}. "
                    "Platform-neutral, clean, and bold."
                )
            },
            {
                "type": "image",
                "prompt_template": (
                    "Create a vertical 9:16 story/reel cover image for Hegay AI with the text: \"{headline}\". "
                    "Use Hegay brand colors and a dynamic layout suitable for TikTok, Reels, and Shorts."
                )
            },
            {
                "type": "video",
                "prompt_template": (
                    "Generate a short vertical promo video (9:16) for Hegay AI about: \"{headline}\". "
                    "Target: social media awareness. "
                    "Style: {visual_style}, tone: {tone}. "
                    "Show fast cuts, UI glimpses, and creators using Hegay."
                ),
                "duration": 10
            }
        ]
    },

    # -----------------------------------------------------
    # ⭐ FLYER / POSTER (EVENT / ANNOUNCEMENT)
    # -----------------------------------------------------
    "flyer": {
        "name": "Hegay Flyer / Poster",
        "description": "Generates a flyer/poster-style promo visual for Hegay AI.",
        "steps": [
            {
                "type": "image",
                "prompt_template": (
                    "Create a high-resolution flyer/poster for Hegay AI with the headline: \"{headline}\" "
                    "and subtext: \"{subtext}\". "
                    "Use Hegay brand colors: {primary_color}, {secondary_color}, {accent_color}. "
                    "Design language: {design_language}. "
                    "Layout should be suitable for both print and digital."
                )
            }
        ]
    },

    # -----------------------------------------------------
    # ⭐ HOMEPAGE BANNER
    # -----------------------------------------------------
    "homepage_banner": {
        "name": "Hegay Homepage Banner",
        "description": "Generates a hero banner visual for the main Hegay landing page.",
        "steps": [
            {
                "type": "image",
                "prompt_template": (
                    "Create a wide hero banner for the Hegay AI homepage with the headline: \"{headline}\" "
                    "and supporting line: \"{subtext}\". "
                    "Use Hegay brand colors and a cinematic, OS-level UI aesthetic. "
                    "Focus on global creators, workflows, and premium design."
                )
            }
        ]
    },

    # -----------------------------------------------------
    # ⭐ DASHBOARD PROMO STRIP
    # -----------------------------------------------------
    "dashboard_promo": {
        "name": "Hegay Dashboard Promo",
        "description": "Generates a promo visual for the dashboard landing area.",
        "steps": [
            {
                "type": "image",
                "prompt_template": (
                    "Create a clean dashboard promo banner for Hegay AI with the text: \"{headline}\". "
                    "Use Hegay brand colors and minimal UI elements that fit into a dashboard card layout."
                )
            }
        ]
    },

    # -----------------------------------------------------
    # ⭐ STUDIO PROMO (INSIDE CREATIVE STUDIO)
    # -----------------------------------------------------
    "studio_promo": {
        "name": "Hegay Studio Promo",
        "description": "Generates a promo visual for the Studio landing page.",
        "steps": [
            {
                "type": "image",
                "prompt_template": (
                    "Create a cinematic studio promo image for Hegay AI Studio with the text: \"{headline}\". "
                    "Show creative tools, timelines, and AI workflows in a premium OS-style interface. "
                    "Use Hegay brand colors and a futuristic, global aesthetic."
                )
            }
        ]
    }
}


# ---------------------------------------------------------
# ⭐ GET ADMIN TEMPLATE BY NAME
# ---------------------------------------------------------
def get_admin_template(name: str):
    return ADMIN_BRAND_WORKFLOW_TEMPLATES.get(name)
