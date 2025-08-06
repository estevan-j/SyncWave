"""
Chat-related Pydantic schemas for validation and serialization
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class ChatMessageCreate(BaseModel):
    """Schema for creating a new chat message"""
    user_id: str = Field(..., description="ID of the user sending the message")
    username: Optional[str] = Field(None, description="Username of the sender")
    message: str = Field(..., min_length=1, max_length=1000,
                         description="Message content")
    room: str = Field(default="general", max_length=50,
                      description="Chat room name")

    @validator('message')
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()

    @validator('room')
    def validate_room(cls, v):
        if not v:
            return "general"
        return v.strip()

    class Config:
        from_attributes = True


class ChatMessageResponse(BaseModel):
    """Schema for chat message responses"""
    id: int = Field(..., description="Message ID")
    user_id: str = Field(...,
                         description="ID of the user who sent the message")
    username: str = Field(..., description="Username of the sender")
    message: str = Field(..., description="Message content")
    timestamp: datetime = Field(..., description="When the message was sent")
    room: str = Field(..., description="Chat room name")

    class Config:
        from_attributes = True


class MessageHistoryResponse(BaseModel):
    """Schema for paginated message history"""
    messages: List[ChatMessageResponse] = Field(
        default=[], description="List of messages")
    total: int = Field(default=0, description="Total number of messages")
    pages: int = Field(default=0, description="Total number of pages")
    current_page: int = Field(default=1, description="Current page number")
    has_next: bool = Field(
        default=False, description="Whether there's a next page")
    has_prev: bool = Field(
        default=False, description="Whether there's a previous page")

    class Config:
        from_attributes = True


class JoinRoomRequest(BaseModel):
    """Schema for joining a chat room"""
    user_id: str = Field(..., description="ID of the user joining")
    username: Optional[str] = Field(None, description="Username of the user")
    room: str = Field(default="general", description="Room to join")

    class Config:
        from_attributes = True


class LeaveRoomRequest(BaseModel):
    """Schema for leaving a chat room"""
    user_id: str = Field(..., description="ID of the user leaving")
    room: str = Field(default="general", description="Room to leave")

    class Config:
        from_attributes = True


class TypingIndicatorRequest(BaseModel):
    """Schema for typing indicator"""
    user_id: str = Field(..., description="ID of the user typing")
    username: Optional[str] = Field(None, description="Username of the user")
    room: str = Field(default="general",
                      description="Room where user is typing")
    is_typing: bool = Field(
        default=False, description="Whether user is typing")

    class Config:
        from_attributes = True


class DeleteMessageRequest(BaseModel):
    """Schema for deleting a message"""
    user_id: str = Field(...,
                         description="ID of the user deleting the message")

    class Config:
        from_attributes = True


class RoomStatistics(BaseModel):
    """Schema for room statistics"""
    room: str = Field(..., description="Room name")
    message_count: int = Field(default=0, description="Total messages in room")
    last_message: Optional[ChatMessageResponse] = Field(
        None, description="Last message in room")

    class Config:
        from_attributes = True
