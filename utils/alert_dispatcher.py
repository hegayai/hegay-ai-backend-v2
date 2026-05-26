from models.admin_alert import AdminAlert
from database import db

def send_admin_alert(alert_type: str, message: str):
    alert = AdminAlert(type=alert_type, message=message)
    db.session.add(alert)
    db.session.commit()
