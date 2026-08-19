from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class IntentType(str, Enum):
    PRODUCT = "PRODUCT"
    ORGANIZATION = "ORGANIZATION"
    MULTI = "MULTI"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None


class SourceInfo(BaseModel):
    type: str
    product_name: Optional[str] = None
    filename: Optional[str] = None
    metadata: Dict[str, Any] = {}


class ChatResponse(BaseModel):
    answer: str
    intent: IntentType
    sources: List[SourceInfo] = []
    session_id: str


class HealthResponse(BaseModel):
    status: str
    service: str = "rag-chatbot"


class ErrorResponse(BaseModel):
    error: Dict[str, str]


class RetrievedDocument(BaseModel):
    content: str
    metadata: Dict[str, Any]
    distance: float