from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.moderation import ModerationRequest, ModerationResult
from app.moderation.pipeline import moderate
from app.services.audit_service import log_moderation
from logger import get_logger
from exception import CustomException

router = APIRouter(prefix="/moderation", tags=["Moderation"])
logger = get_logger(__name__)

@router.post("/check", response_model=ModerationResult)
def check_moderation(payload: ModerationRequest, db: Session = Depends(get_db)):
    try:
        result = moderate(payload.text)
        log_moderation(db, payload.text, result)
        return result
    except Exception as exc:
        logger.exception("Moderation endpoint failed")
        if isinstance(exc, CustomException):
            raise
        raise CustomException("Moderation request failed", exc)
