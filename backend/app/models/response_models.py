from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str
    intent: str
    metrics: Dict[str, Any]
    warnings: List[str] = []
    sources: List[str] = []
