from app.moderation.rules import evaluate_rules

def test_clean_message_is_allowed():
    result = evaluate_rules("Hello, can you help with my order?")
    assert result["action"] == "allow"
    assert result["category"] == "clean"

def test_profanity_is_blocked():
    result = evaluate_rules("you are a fucking idiot")
    assert result["action"] == "block"
    assert result["category"] == "profanity"

def test_url_is_reviewed_not_automatically_blocked():
    result = evaluate_rules("Please see https://example.com")
    assert result["action"] == "review_required"
