import time
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.moderation.pipeline import moderate
from app.services.intent_service import detect_intent
from app.agents.registry import route_intent
from app.db.models import ChatLog, User
from app.core.security import get_optional_current_user
from app.services.audit_service import log_moderation
from logger import get_logger
from exception import CustomException

router = APIRouter(prefix="/chat", tags=["Customer Support"])
logger = get_logger(__name__)

@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db), current_user: User | None = Depends(get_optional_current_user)):
    started = time.perf_counter()
    request_id = str(uuid.uuid4())
    try:
        moderation = moderate(payload.message)
        log_moderation(db, payload.message, moderation)
        if moderation["action"] == "block":
            answer = "I can't help process that message because it violates the support conversation policy. Please rephrase your request."
            intent = "blocked"
            source = moderation["source"]
        elif moderation["action"] == "review_required":
            answer = "This message needs a safety review before I can process it. Please rephrase without links or repeated promotional text."
            intent = "review_required"
            source = moderation["source"]
        else:
            detected = detect_intent(payload.message)
            intent = detected["intent"]
            answer = route_intent(intent, payload.message, db, current_user.id if current_user else None)
            source = detected["source"]
        elapsed = (time.perf_counter() - started) * 1000
        db.add(ChatLog(user_id=current_user.id if current_user else None, message=payload.message, response=answer, intent=intent,
                       moderation_action=moderation["action"], latency_ms=elapsed))
        db.commit()
        return ChatResponse(response=answer, intent=intent, moderation_action=moderation["action"],
                            source=source, request_id=request_id)
    except CustomException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("Chat endpoint failed request_id=%s", request_id)
        raise CustomException("Chat request failed", exc)
