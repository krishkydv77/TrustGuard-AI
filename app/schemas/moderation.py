from pydantic import BaseModel, Field
from typing import Literal

class ModerationRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10000)

class ModerationResult(BaseModel):
    category: str
    action: Literal["allow", "block", "review_required"]
    confidence: float = Field(ge=0, le=1)
    reason: str
    source: str
