from models.chat_memory import ChatMemory
from database import db
from datetime import datetime

def remember(user_id: int, key: str, value: str):
    entry = ChatMemory.query.filter_by(user_id=user_id, key=key).first()
    if entry:
        entry.value = value
        entry.updated_at = datetime.utcnow()
    else:
        entry = ChatMemory(user_id=user_id, key=key, value=value)
        db.session.add(entry)
    db.session.commit()

def recall(user_id: int, key: str):
    entry = ChatMemory.query.filter_by(user_id=user_id, key=key).first()
    return entry.value if entry else None

def recall_all(user_id: int):
    entries = ChatMemory.query.filter_by(user_id=user_id).all()
    return {e.key: e.value for e in entries}
