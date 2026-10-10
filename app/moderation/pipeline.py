from app.moderation.rules import evaluate_rules
from app.moderation.llm_moderator import moderate_with_gemini
from app.core.config import settings
from logger import get_logger
from exception import CustomException

logger = get_logger(__name__)

def moderate(text: str) -> dict:
    try:
        result = evaluate_rules(text)
        # Hard rules can immediately block; clean/ambiguous results can be enriched by Gemini.
        if result["action"] == "block":
            return result
        llm_result = moderate_with_gemini(text)
        if llm_result is None:
            return result
        # Do not let a low-confidence LLM response silently override a clear rule-based review.
        if result["action"] == "review_required" and llm_result["confidence"] < settings.moderation_review_threshold:
            return result
        return llm_result
    except Exception as exc:
        logger.exception("Moderation pipeline failed closed")
        raise CustomException("Moderation pipeline failed", exc)
