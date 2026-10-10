import re
from logger import get_logger
from exception import CustomException

logger = get_logger(__name__)

# Replace/extend these with a reviewed, language-aware policy wordlist.
PROFANITY_TERMS = {
    "fuck", "fucking", "shit", "bitch", "asshole",
    "madarchod", "bhenchod", "chutiya", "gaand","bsdk","sale kutte"
}
URL_RE = re.compile(r"(https?://|www\.)\S+", re.IGNORECASE)
REPEATED_CHAR_RE = re.compile(r"(.)\1{9,}", re.IGNORECASE)
SPAM_PHRASES = ("buy followers", "free crypto", "click here to claim", "earn money fast")

def normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())

def evaluate_rules(text: str) -> dict:
    try:
        normalized = normalize(text)
        tokens = set(re.findall(r"[a-zA-Z]+|[\u0900-\u097F]+", normalized))
        if any(term in tokens for term in PROFANITY_TERMS):
            return {"category": "profanity", "action": "block", "confidence": 0.96,
                    "reason": "Matched a configured profanity term.", "source": "rules"}
        if any(phrase in normalized for phrase in SPAM_PHRASES) or REPEATED_CHAR_RE.search(normalized):
            return {"category": "spam", "action": "review_required", "confidence": 0.82,
                    "reason": "Message matched a spam heuristic.", "source": "rules"}
        if URL_RE.search(normalized):
            return {"category": "link_present", "action": "review_required", "confidence": 0.65,
                    "reason": "Message contains a URL; link alone is not proof of abuse.", "source": "rules"}
        return {"category": "clean", "action": "allow", "confidence": 0.72,
                "reason": "No configured high-risk rule matched.", "source": "rules"}
    except Exception as exc:
        logger.exception("Rule-based moderation failed")
        raise CustomException("Rule-based moderation failed", exc)
