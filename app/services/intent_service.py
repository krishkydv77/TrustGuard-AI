import json
from app.core.config import settings
from logger import get_logger
from exception import CustomException

logger = get_logger(__name__)
VALID_INTENTS = {"account", "order_status", "refund", "product", "complaint", "general"}

def detect_intent(message: str) -> dict:
    text = message.lower()
    if any(x in text for x in ("refund", "return", "money back", "paise wapas")):
        return {"intent": "refund", "source": "rules", "confidence": 0.8}
    if any(x in text for x in ("where is my order", "order status", "track order", "mera order", "delivery")):
        return {"intent": "order_status", "source": "rules", "confidence": 0.8}
    if any(x in text for x in ("account", "login", "password", "sign up", "register")):
        return {"intent": "account", "source": "rules", "confidence": 0.75}
    if any(x in text for x in ("product", "item", "price", "feature")):
        return {"intent": "product", "source": "rules", "confidence": 0.7}
    if any(x in text for x in ("complaint", "bad service", "unhappy", "problem", "issue")):
        return {"intent": "complaint", "source": "rules", "confidence": 0.7}
    if not settings.gemini_api_key:
        return {"intent": "general", "source": "rules", "confidence": 0.55}
    try:
        from google import genai
        client = genai.Client(api_key=settings.gemini_api_key)
        prompt = ("Classify intent as one of account, order_status, refund, product, complaint, general. "
                  "Return JSON only: {intent, confidence}. User message: " + json.dumps(message, ensure_ascii=False))
        response = client.models.generate_content(model=settings.gemini_model, contents=prompt,
                                                  config={"response_mime_type": "application/json"})
        data = json.loads(response.text or "{}")
        intent = data.get("intent", "general")
        if intent not in VALID_INTENTS:
            intent = "general"
        return {"intent": intent, "source": "gemini", "confidence": max(0, min(1, float(data.get("confidence", .5))))}
    except Exception:
        logger.exception("Intent LLM failed; falling back to general")
        return {"intent": "general", "source": "fallback", "confidence": 0.3}
