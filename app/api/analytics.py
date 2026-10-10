from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.db.models import ChatLog, ModerationEvent
from logger import get_logger
from exception import CustomException

router = APIRouter(prefix="/analytics", tags=["Analytics"])
logger = get_logger(__name__)

@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    try:
        total_chats = db.query(func.count(ChatLog.id)).scalar() or 0
        total_moderation = db.query(func.count(ModerationEvent.id)).scalar() or 0
        actions = dict(db.query(ModerationEvent.action, func.count(ModerationEvent.id)).group_by(ModerationEvent.action).all())
        avg_latency = db.query(func.avg(ChatLog.latency_ms)).scalar() or 0
        return {"total_chats": total_chats, "moderation_checks": total_moderation,
                "moderation_actions": actions, "average_chat_latency_ms": round(float(avg_latency), 2)}
    except Exception as exc:
        logger.exception("Analytics query failed")
        raise CustomException("Could not load analytics", exc)
