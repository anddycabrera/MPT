from pydantic import BaseModel
from typing import List, Optional

class Completion(BaseModel):
    model: str
    prompt: str
    temperature: Optional[float] = 0.0
    max_tokens: Optional[int] = 4096
    top_p: Optional[float] = 1.0
    frequency_penalty: Optional[float] = 0.0
    presence_penalty: Optional[float] = 0.0
    stop: Optional[List[str]]

class ChatAIRequest(BaseModel):
    question: str
    session_id: str