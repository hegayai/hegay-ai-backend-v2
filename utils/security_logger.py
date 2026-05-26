from models.security_log import SecurityLog
from database import db
from flask import request, session
from utils.alert_dispatcher import send_admin_alert

def log_security_event(event: str):
    actor = session.get("email", "unknown")
    ip = request.remote_addr
    agent = request.headers.get("User-Agent")

    log = SecurityLog(
        event=event,
        actor=actor,
        ip=ip,
        user_agent=agent
    )

    db.session.add(log)
    db.session.commit()

    # ⭐ Trigger admin alert
    send_admin_alert("security", event)
