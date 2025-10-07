# app/utils/logger.py
from app.models.log.logs import Logs
from datetime import datetime

def create_log(db, user_id: int, action: str, entity: str = None, entity_id: int = None, description: str = None):
    new_log = Logs(
        user_id=user_id,
        action=action,
        entity=entity,
        entity_id=entity_id,
        description=description,
        created_at=datetime.utcnow()
    )
    db.add(new_log)
    db.commit()
    