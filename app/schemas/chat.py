from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=10000)

class ChatResponse(BaseModel):
    response: str
    intent: str
    moderation_action: str
    source: str
    request_id: str
