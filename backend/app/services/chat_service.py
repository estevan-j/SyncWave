from flask_socketio import emit, join_room, leave_room
from app.models.database import db, ChatMessage, User
from datetime import datetime

class ChatService:
    @staticmethod
    def save_message(user_id, message, room='general'):
        """Save a chat message to the database"""
        try:
            chat_message = ChatMessage(
                user_id=user_id,
                message=message,
                room=room,
                timestamp=datetime.utcnow()
            )
            db.session.add(chat_message)
            db.session.commit()
            return chat_message
        except Exception as e:
            db.session.rollback()
            return None
    
    @staticmethod
    def get_recent_messages(room='general', limit=50):
        """Get recent messages from a chat room"""
        try:
            messages = ChatMessage.query.filter_by(room=room)\
                                      .order_by(ChatMessage.timestamp.desc())\
                                      .limit(limit)\
                                      .all()
            return [msg.to_dict() for msg in reversed(messages)]
        except Exception as e:
            return []
    
    @staticmethod
    def get_message_history(room='general', page=1, per_page=20):
        """Get paginated message history"""
        try:
            messages = ChatMessage.query.filter_by(room=room)\
                                      .order_by(ChatMessage.timestamp.desc())\
                                      .paginate(
                                          page=page,
                                          per_page=per_page,
                                          error_out=False
                                      )
            return {
                'messages': [msg.to_dict() for msg in reversed(messages.items)],
                'total': messages.total,
                'pages': messages.pages,
                'current_page': page,
                'has_next': messages.has_next,
                'has_prev': messages.has_prev
            }
        except Exception as e:
            return {
                'messages': [],
                'total': 0,
                'pages': 0,
                'current_page': 1,
                'has_next': False,
                'has_prev': False
            }
    
    @staticmethod
    def validate_message_data(data):
        """Validate chat message data"""
        errors = []
        
        if not data.get('message'):
            errors.append('Message is required')
        elif len(data.get('message', '').strip()) == 0:
            errors.append('Message cannot be empty')
        elif len(data.get('message', '')) > 1000:
            errors.append('Message cannot exceed 1000 characters')
            
        if not data.get('user_id'):
            errors.append('User ID is required')
            
        room = data.get('room', 'general')
        if len(room) > 50:
            errors.append('Room name cannot exceed 50 characters')
            
        return errors
    
    @staticmethod
    def get_active_rooms():
        """Get list of active chat rooms"""
        try:
            rooms = db.session.query(ChatMessage.room)\
                             .distinct()\
                             .filter(ChatMessage.room.isnot(None))\
                             .all()
            return [room[0] for room in rooms]
        except Exception as e:
            return ['general']
    
    @staticmethod
    def delete_message(message_id, user_id):
        """Delete a message (only by the author)"""
        try:
            message = ChatMessage.query.filter_by(id=message_id, user_id=user_id).first()
            if message:
                db.session.delete(message)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            return False
