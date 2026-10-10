from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.config import settings
from logger import get_logger
from exception import CustomException

router = APIRouter(tags=["Health"])
logger = get_logger(__name__)

@router.get("/health/live")
def live():
    return {"status": "alive", "service": settings.app_name}

@router.get("/health/ready")
def ready(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as exc:
        logger.exception("Readiness check failed")
        raise CustomException("Service is not ready", exc)
