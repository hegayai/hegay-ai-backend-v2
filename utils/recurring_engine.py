from datetime import datetime, timedelta
from database import db
from models.recurring_promo import RecurringPromo
from utils.auto_publish_engine import publish_promo

WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

# ---------------------------------------------------------
# WEEKLY
# ---------------------------------------------------------
def should_run_weekly(rp: RecurringPromo, now: datetime):
    target_day = WEEKDAYS.get(rp.recurrence_value.lower())
    if target_day is None:
        return False

    if now.weekday() != target_day:
        return False

    if rp.last_executed and rp.last_executed.date() == now.date():
        return False

    return True

# ---------------------------------------------------------
# INTERVAL (every X days)
# ---------------------------------------------------------
def should_run_interval(rp: RecurringPromo, now: datetime):
    days = int(rp.recurrence_value)
    if not rp.last_executed:
        return True

    return (now - rp.last_executed) >= timedelta(days=days)

# ---------------------------------------------------------
# DAILY
# ---------------------------------------------------------
def should_run_daily(rp: RecurringPromo, now: datetime):
    if rp.last_executed and rp.last_executed.date() == now.date():
        return False
    return True

# ---------------------------------------------------------
# MONTHLY
# recurrence_value:
#   "1" → 1st of month
#   "15" → 15th of month
#   "last" → last day of month
# ---------------------------------------------------------
def should_run_monthly(rp: RecurringPromo, now: datetime):
    # Last day of month
    if rp.recurrence_value == "last":
        next_day = now + timedelta(days=1)
        is_last_day = next_day.month != now.month

        if not is_last_day:
            return False

        if rp.last_executed and rp.last_executed.date() == now.date():
            return False

        return True

    # Specific day of month (1–28)
    try:
        target_day = int(rp.recurrence_value)
    except:
        return False

    if now.day != target_day:
        return False

    if rp.last_executed and rp.last_executed.date() == now.date():
        return False

    return True

# ---------------------------------------------------------
# MAIN ENGINE
# ---------------------------------------------------------
def run_recurring_promos():
    now = datetime.utcnow()
    promos = RecurringPromo.query.all()
    executed = []

    for rp in promos:
        run = False

        if rp.recurrence_type == "weekly":
            run = should_run_weekly(rp, now)

        elif rp.recurrence_type == "interval":
            run = should_run_interval(rp, now)

        elif rp.recurrence_type == "daily":
            run = should_run_daily(rp, now)

        elif rp.recurrence_type == "monthly":
            run = should_run_monthly(rp, now)

        if run:
            publish_promo(
                location=rp.location,
                title=rp.title or "",
                subtitle=rp.subtitle or "",
                asset_url=rp.asset_url,
                asset_type=rp.asset_type,
                language=rp.language,
            )

            rp.last_executed = now
            executed.append(rp)

    if executed:
        db.session.commit()

    return executed
