# ---------------------------------------------------------
# ⭐ HEGAY WORKFLOW TEMPLATES (FINAL VERSION)
# ---------------------------------------------------------

WORKFLOW_TEMPLATES = {
    # -----------------------------------------------------
    # ⭐ CINEMATIC WORKFLOW
    # -----------------------------------------------------
    "cinematic": {
        "name": "Cinematic Video Workflow",
        "description": "Creates a cinematic sequence including character, motion, and final video.",
        "steps": [
            {
                "type": "image",
                "prompt_template": "Create a cinematic portrait of {subject} in {style} lighting."
            },
            {
                "type": "motion",
                "reference_template": "Apply cinematic motion style: {motion_style}"
            },
            {
                "type": "video",
                "prompt_template": "Generate a cinematic intro video featuring {subject} with {theme} theme.",
                "duration": 5
            }
        ]
    },

    # -----------------------------------------------------
    # ⭐ FOOTBALL WORKFLOW
    # -----------------------------------------------------
    "football": {
        "name": "Football Highlight Workflow",
        "description": "Creates football player visuals, motion, and highlight reels.",
        "steps": [
            {
                "type": "image",
                "prompt_template": "Create a hyper‑realistic football portrait of {player_name} in {team_colors}."
            },
            {
                "type": "motion",
                "reference_template": "Apply football movement: {movement_type}"
            },
            {
                "type": "video",
                "prompt_template": "Generate a football highlight intro for {player_name} with {energy_level} energy.",
                "duration": 7
            }
        ]
    },

    # -----------------------------------------------------
    # ⭐ DANCE WORKFLOW
    # -----------------------------------------------------
    "dance": {
        "name": "Dance Motion Workflow",
        "description": "Creates dance visuals, applies motion, and outputs a dance clip.",
        "steps": [
            {
                "type": "image",
                "prompt_template": "Create a stylized dance character in {style} aesthetic."
            },
            {
                "type": "motion",
                "reference_template": "Apply dance motion: {dance_style}"
            },
            {
                "type": "video",
                "prompt_template": "Generate a dance performance video with {vibe} mood.",
                "duration": 6
            }
        ]
    },

    # -----------------------------------------------------
    # ⭐ BRANDING / ADVERTISING WORKFLOW
    # -----------------------------------------------------
    "branding": {
        "name": "Brand Advertisement Workflow",
        "description": "Creates brand visuals, product shots, and promotional videos.",
        "steps": [
            {
                "type": "image",
                "prompt_template": (
                    "Create a premium product image for {brand_name} featuring {product_name} "
                    "in {visual_style} style for marketing and advertisement."
                )
            },
            {
                "type": "image",
                "prompt_template": (
                    "Create a brand identity background for {brand_name} using {color_palette} "
                    "and {design_language}."
                )
            },
            {
                "type": "video",
                "prompt_template": (
                    "Generate a promotional advert video for {brand_name} showcasing {product_name} "
                    "with {selling_point} and {tone} tone."
                ),
                "duration": 8
            }
        ]
    }
}


# ---------------------------------------------------------
# ⭐ GET TEMPLATE BY NAME
# ---------------------------------------------------------
def get_template(name: str):
    return WORKFLOW_TEMPLATES.get(name)
