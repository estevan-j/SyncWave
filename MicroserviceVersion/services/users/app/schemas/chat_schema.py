from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatMessageCreate(BaseModel):
    """Schema for creating a new chat message"""
    message: str = Field(..., min_length=1, max_length=1000, description="The message content")
    room: str = Field(default="general", max_length=50, description="The chat room name")
    user_id: str = Field(..., description="The user ID who sent the message")
    username: Optional[str] = Field(None, description="The username of the sender")


class ChatMessageResponse(BaseModel):
    """Schema for chat message response"""
    id: int
    user_id: str
    username: str
    message: str
    timestamp: datetime
    room: str

    class Config:
        from_attributes = True


class ChatRoomResponse(BaseModel):
    """Schema for chat room information"""
    name: str
    message_count: int
    last_message: Optional[ChatMessageResponse] = None


class MessageHistoryResponse(BaseModel):
    """Schema for paginated message history"""
    messages: List[ChatMessageResponse]
    total: int
    pages: int
    current_page: int
    has_next: bool
    has_prev: bool


class JoinRoomRequest(BaseModel):
    """Schema for joining a chat room"""
    user_id: str = Field(..., description="The user ID")
    room: str = Field(default="general", max_length=50, description="The room to join")
    username: Optional[str] = Field(None, description="The username")


class LeaveRoomRequest(BaseModel):
    """Schema for leaving a chat room"""
    user_id: str = Field(..., description="The user ID")
    room: str = Field(default="general", max_length=50, description="The room to leave")


class TypingIndicatorRequest(BaseModel):
    """Schema for typing indicator"""
    user_id: str = Field(..., description="The user ID")
    room: str = Field(default="general", max_length=50, description="The room")
    is_typing: bool = Field(..., description="Whether the user is typing")


class DeleteMessageRequest(BaseModel):
    """Schema for deleting a message"""
    user_id: str = Field(..., description="The user ID who wants to delete the message")
    message_id: int = Field(..., description="The message ID to delete") 