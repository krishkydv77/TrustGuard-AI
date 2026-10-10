import hashlib
from sqlalchemy.orm import Session
from app.db.models import ModerationEvent
from logger import get_logger
from exception import CustomException

logger = get_logger(__name__)

def log_moderation(db: Session, text: str, result: dict) -> None:
    try:
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        db.add(ModerationEvent(message_hash=digest, category=result["category"], action=result["action"],
                               confidence=result["confidence"], reason=result["reason"]))
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.exception("Could not persist moderation event")
        raise CustomException("Could not persist moderation audit event", exc)
