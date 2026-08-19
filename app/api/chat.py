from fastapi import APIRouter, HTTPException
from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import chat_service
from app.core.logging import logger


router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = await chat_service.process_chat(request)
        return response
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail={
            "error": {
                "code": "CHAT_ERROR",
                "message": "Unable to process chat request"
            }
        })