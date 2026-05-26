import secrets
import hashlib
from datetime import datetime
from database import db
from models.api_key import ApiKey
from models.api_usage import ApiUsage

def generate_api_key(label: str):
    raw_key = secrets.token_hex(32)
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

    entry = ApiKey(
        key_hash=key_hash,
        label=label
    )
    db.session.add(entry)
    db.session.commit()

    return raw_key  # only returned once


def revoke_api_key(key_id: int):
    key = ApiKey.query.get(key_id)
    if not key:
        return False

    key.revoked = True
    db.session.commit()
    return True


def record_key_usage(key_hash: str, status_code: int, latency_ms: int):
    key = ApiKey.query.filter_by(key_hash=key_hash).first()
    if not key:
        return

    key.usage_count += 1
    key.last_used = datetime.utcnow()

    usage = ApiUsage(
        api_key_id=key.id,
        status_code=status_code,
        latency_ms=latency_ms,
    )

    db.session.add(usage)
    db.session.commit()
