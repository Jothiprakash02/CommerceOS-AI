"""
Chat Assistant Schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class ChatMessage(BaseModel):
    """Single chat message"""
    role: str = Field(..., description="user or assistant")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Chat request from user"""
    message: str = Field(..., description="User's message")
    conversation_history: List[ChatMessage] = Field(
        default_factory=list,
        description="Previous conversation for context"
    )
    current_page: Optional[str] = Field(
        None,
        description="Current page user is on (discover, analyze, results, etc.)"
    )
    user_context: Optional[dict] = Field(
        None,
        description="Additional context (current analysis data, etc.)"
    )


class ChatResponse(BaseModel):
    """Chat response from assistant"""
    message: str = Field(..., description="Assistant's response")
    suggestions: List[str] = Field(
        default_factory=list,
        description="Suggested follow-up questions"
    )
    action: Optional[str] = Field(
        None,
        description="Suggested action (navigate_to, run_analysis, etc.)"
    )
    action_data: Optional[dict] = Field(
        None,
        description="Data for the suggested action"
    )
