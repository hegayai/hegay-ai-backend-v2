from pricing.credits import (
    CREDITS_PER_IMAGE,
    CREDITS_PER_CANVAS_ACTION,
    credits_for_video,
    MOTION_CREDITS_PER_SECOND,
    REELS_CREDITS_PER_SECOND,
    BRANDING_SUITE_CREDITS
)

def calculate_credit_usage(feature_type, **kwargs):
    if feature_type == "image":
        return CREDITS_PER_IMAGE

    if feature_type == "canvas":
        return CREDITS_PER_CANVAS_ACTION

    if feature_type == "video":
        seconds = kwargs.get("seconds", 1)
        resolution = kwargs.get("resolution", "720p")
        return credits_for_video(seconds, resolution)

    if feature_type == "motion":
        seconds = kwargs.get("seconds", 1)
        return seconds * MOTION_CREDITS_PER_SECOND

    if feature_type == "reels":
        seconds = kwargs.get("seconds", 1)
        return seconds * REELS_CREDITS_PER_SECOND

    if feature_type == "branding":
        return BRANDING_SUITE_CREDITS

    return 0
