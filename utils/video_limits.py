def get_max_video_seconds(user):
    """
    Returns the maximum allowed video duration for a user.
    Admins get a 30-minute override.
    All other users follow their plan limits.
    """

    # ⭐ Admin override: 30 minutes (1800 seconds)
    if user.role == "admin":
        return 1800

    # Normalize plan name (Free, Starter, Creator, Pro, Studio)
    plan = (user.plan or "Free").strip().title()

    # ⭐ Safe plan limits (Category A)
    plan_limits = {
        "Free": 0,
        "Starter": 5,
        "Creator": 6,
        "Pro": 8,
        "Studio": 10
    }

    # ⭐ Always return a valid number
    return plan_limits.get(plan, 0)
