# pricing/credits.py

# -----------------------------
# CREDIT PACKS (GBP, matches Stripe)
# -----------------------------

CREDIT_PACKS = {
    100: 20,     # £20
    300: 50,     # £50
    600: 90,     # £90
    1200: 160    # £160
}

COST_PER_CREDIT = {
    100: CREDIT_PACKS[100] / 100,     # £0.20
    300: CREDIT_PACKS[300] / 300,     # ≈ £0.1667
    600: CREDIT_PACKS[600] / 600,     # £0.15
    1200: CREDIT_PACKS[1200] / 1200   # ≈ £0.1333
}

# -----------------------------
# CREDIT USAGE RULES
# -----------------------------

CREDITS_PER_IMAGE = 1
CREDITS_PER_CANVAS_ACTION = 2

VIDEO_CREDIT_MULTIPLIER = {
    "480p": 1,
    "720p": 2,
    "1080p": 3
}

def credits_for_video(seconds: int, resolution: str) -> int:
    multiplier = VIDEO_CREDIT_MULTIPLIER.get(resolution, 2)
    return seconds * multiplier

MOTION_CREDITS_PER_SECOND = 5
REELS_CREDITS_PER_SECOND = 8
BRANDING_SUITE_CREDITS = 15
