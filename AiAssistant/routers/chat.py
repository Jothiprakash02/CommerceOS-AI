"""
Chat Assistant Router
"""

import logging
import sys
import os

# Path setup
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
for _p in [_ROOT, os.path.join(_ROOT, "global")]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from fastapi import APIRouter, HTTPException
from AiAssistant.schemas.chat_schema import ChatRequest, ChatResponse
from AiAssistant.services.gemini_service import get_assistant

log = logging.getLogger(__name__)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(request: ChatRequest):
    """
    Chat with the AI assistant.
    
    The assistant can:
    - Answer questions about MarketMind features
    - Explain e-commerce terminology
    - Guide users through workflows
    - Provide analysis insights
    - Suggest next steps
    
    Context-aware based on current page and conversation history.
    """
    try:
        log.info(
            "Chat request: page=%s message=%s",
            request.current_page,
            request.message[:50]
        )
        
        # Get assistant instance
        assistant = get_assistant()
        
        # Convert Pydantic models to dicts
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.conversation_history
        ]
        
        # Get response
        result = await assistant.chat(
            user_message=request.message,
            conversation_history=history,
            current_page=request.current_page,
            user_context=request.user_context
        )
        
        return ChatResponse(
            message=result["message"],
            suggestions=result["suggestions"],
            action=result["action"],
            action_data=result["action_data"]
        )
        
    except ValueError as ve:
        # API key not configured
        log.error(f"Configuration error: {ve}")
        raise HTTPException(
            status_code=503,
            detail=str(ve)
        )
    
    except Exception as exc:
        log.error(f"Chat failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Chat failed: {str(exc)}"
        )


@router.get("/chat/health")
async def chat_health():
    """Check if chat assistant is configured and ready"""
    try:
        assistant = get_assistant()
        return {
            "status": "ready",
            "model": "gemini-1.5-flash",
            "message": "Chat assistant is ready"
        }
    except ValueError as ve:
        return {
            "status": "not_configured",
            "message": str(ve)
        }
    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc)
        }
