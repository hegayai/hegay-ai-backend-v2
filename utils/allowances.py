from pricing.plans import PLANS

def get_plan_allowances(plan_name: str):
    """
    Safely return the allowance configuration for a given plan.
    Falls back to Free plan if the plan does not exist.
    Handles case-insensitive plan names.
    """
    if not plan_name:
        return PLANS["Free"]

    # Normalize plan name (Free, Starter, Creator, Pro, Studio)
    normalized = str(plan_name).strip().title()

    return PLANS.get(normalized, PLANS["Free"])
