"""
Chat service for handling chat operations with Supabase
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.core.supabase import get_supabase, get_supabase_admin
from app.schemas.chat_schema import ChatMessageCreate, ChatMessageResponse, MessageHistoryResponse
from app.exceptions.chat_exceptions import (
    MessageValidationException,
    MessageNotFoundException,
    UnauthorizedMessageException,
    ChatServiceException
)
import logging

logger = logging.getLogger("chat_service")


class ChatService:
    """Service class for chat-related operations"""

    def __init__(self):
        self.supabase = get_supabase()
        self.supabase_admin = get_supabase_admin()

    def save_message(self, message_data: ChatMessageCreate) -> ChatMessageResponse:
        """Save a chat message to the database"""
        try:
            # Validate message data
            self._validate_message_data(message_data)
            
            # Prepare data for Supabase
            message_record = {
                'user_id': message_data.user_id,
                'message': message_data.message.strip(),
                'room': message_data.room,
                'timestamp': datetime.utcnow().isoformat(),
                'username': message_data.username or f'User_{message_data.user_id}'
            }
            
            # Insert into chat_messages table
            response = self.supabase_admin.table('chat_messages').insert(message_record).execute()
            
            if not response.data:
                raise ChatServiceException("Failed to save message")
            
            saved_message = response.data[0]
            
            return ChatMessageResponse(
                id=saved_message['id'],
                user_id=saved_message['user_id'],
                username=saved_message['username'],
                message=saved_message['message'],
                timestamp=datetime.fromisoformat(saved_message['timestamp']),
                room=saved_message['room']
            )
            
        except Exception as e:
            logger.error(f"Error saving message: {str(e)}")
            if isinstance(e, (MessageValidationException, ChatServiceException)):
                raise
            raise ChatServiceException(f"Failed to save message: {str(e)}")

    def get_recent_messages(self, room: str = 'general', limit: int = 50) -> List[ChatMessageResponse]:
        """Get recent messages from a chat room"""
        try:
            response = self.supabase_admin.table('chat_messages')\
                .select('*')\
                .eq('room', room)\
                .order('timestamp', desc=False)\
                .limit(limit)\
                .execute()
            
            messages = []
            for msg in response.data:
                messages.append(ChatMessageResponse(
                    id=msg['id'],
                    user_id=msg['user_id'],
                    username=msg['username'],
                    message=msg['message'],
                    timestamp=datetime.fromisoformat(msg['timestamp']),
                    room=msg['room']
                ))
            
            return messages
            
        except Exception as e:
            logger.error(f"Error getting recent messages: {str(e)}")
            return []

    def get_message_history(self, room: str = 'general', page: int = 1, per_page: int = 20) -> MessageHistoryResponse:
        """Get paginated message history"""
        try:
            # Calculate offset for pagination
            offset = (page - 1) * per_page
            
            # Get total count
            count_response = self.supabase_admin.table('chat_messages')\
                .select('id', count='exact')\
                .eq('room', room)\
                .execute()
            
            total = count_response.count or 0
            
            # Get paginated messages
            response = self.supabase_admin.table('chat_messages')\
                .select('*')\
                .eq('room', room)\
                .order('timestamp', desc=True)\
                .range(offset, offset + per_page - 1)\
                .execute()
            
            messages = []
            for msg in response.data:
                messages.append(ChatMessageResponse(
                    id=msg['id'],
                    user_id=msg['user_id'],
                    username=msg['username'],
                    message=msg['message'],
                    timestamp=datetime.fromisoformat(msg['timestamp']),
                    room=msg['room']
                ))
            
            # Reverse to get chronological order
            messages.reverse()
            
            pages = (total + per_page - 1) // per_page if total > 0 else 0
            
            return MessageHistoryResponse(
                messages=messages,
                total=total,
                pages=pages,
                current_page=page,
                has_next=page < pages,
                has_prev=page > 1
            )
            
        except Exception as e:
            logger.error(f"Error getting message history: {str(e)}")
            return MessageHistoryResponse(
                messages=[],
                total=0,
                pages=0,
                current_page=1,
                has_next=False,
                has_prev=False
            )

    def delete_message(self, message_id: int, user_id: str) -> bool:
        """Delete a message (only by the author)"""
        try:
            # First, get the message to check ownership
            response = self.supabase_admin.table('chat_messages')\
                .select('*')\
                .eq('id', message_id)\
                .execute()
            
            if not response.data:
                raise MessageNotFoundException("Message not found")
            
            message = response.data[0]
            
            # Check if user is the author
            if message['user_id'] != user_id:
                raise UnauthorizedMessageException("You can only delete your own messages")
            
            # Delete the message
            delete_response = self.supabase_admin.table('chat_messages')\
                .delete()\
                .eq('id', message_id)\
                .execute()
            
            return len(delete_response.data) > 0
            
        except Exception as e:
            logger.error(f"Error deleting message: {str(e)}")
            if isinstance(e, (MessageNotFoundException, UnauthorizedMessageException)):
                raise
            raise ChatServiceException(f"Failed to delete message: {str(e)}")

    def get_active_rooms(self) -> List[str]:
        """Get list of active chat rooms"""
        try:
            response = self.supabase_admin.table('chat_messages')\
                .select('room')\
                .execute()
            
            rooms = set()
            for msg in response.data:
                if msg.get('room'):
                    rooms.add(msg['room'])
            
            return list(rooms) if rooms else ['general']
            
        except Exception as e:
            logger.error(f"Error getting active rooms: {str(e)}")
            return ['general']

    def _validate_message_data(self, message_data: ChatMessageCreate):
        """Validate chat message data"""
        errors = []
        
        if not message_data.message:
            errors.append('Message is required')
        elif len(message_data.message.strip()) == 0:
            errors.append('Message cannot be empty')
        elif len(message_data.message) > 1000:
            errors.append('Message cannot exceed 1000 characters')
            
        if not message_data.user_id:
            errors.append('User ID is required')
            
        if len(message_data.room) > 50:
            errors.append('Room name cannot exceed 50 characters')
            
        if errors:
            raise MessageValidationException('; '.join(errors))

    def get_room_statistics(self, room: str = 'general') -> Dict[str, Any]:
        """Get statistics for a specific room"""
        try:
            # Get message count
            count_response = self.supabase_admin.table('chat_messages')\
                .select('id', count='exact')\
                .eq('room', room)\
                .execute()
            
            message_count = count_response.count or 0
            
            # Get last message
            last_message_response = self.supabase_admin.table('chat_messages')\
                .select('*')\
                .eq('room', room)\
                .order('timestamp', desc=True)\
                .limit(1)\
                .execute()
            
            last_message = None
            if last_message_response.data:
                msg = last_message_response.data[0]
                last_message = ChatMessageResponse(
                    id=msg['id'],
                    user_id=msg['user_id'],
                    username=msg['username'],
                    message=msg['message'],
                    timestamp=datetime.fromisoformat(msg['timestamp']),
                    room=msg['room']
                )
            
            return {
                'room': room,
                'message_count': message_count,
                'last_message': last_message
            }
            
        except Exception as e:
            logger.error(f"Error getting room statistics: {str(e)}")
            return {
                'room': room,
                'message_count': 0,
                'last_message': None
            } 