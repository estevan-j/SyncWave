"""
WebSocket controller for real-time chat functionality
"""
from flask import request, g
from flask_socketio import emit, join_room, leave_room, disconnect
from app.schemas.chat_schema import ChatMessageCreate
from app.services.chat_service import ChatService
from app.exceptions.chat_exceptions import (
    MessageValidationException,
    ChatServiceException
)
import logging

# Logger
logger = logging.getLogger("websocket_controller")

# Instancia del servicio
chat_service = ChatService()

# Diccionario para mantener usuarios conectados
connected_users = {}

def handle_connect():
    """Handle client connection"""
    try:
        request_id = getattr(g, 'request_id', 'unknown')
        logger.info(f"Client connected: {request.sid}", extra={
            'custom_request_id': request_id
        })
        emit('status', {'msg': f'{request.sid} has connected'})
    except Exception as e:
        logger.error(f"Error in connect handler: {str(e)}")

def handle_disconnect():
    """Handle client disconnection"""
    try:
        request_id = getattr(g, 'request_id', 'unknown')
        
        # Remove user from connected users if exists
        user_to_remove = None
        for user_id, session_id in connected_users.items():
            if session_id == request.sid:
                user_to_remove = user_id
                break
        
        if user_to_remove:
            del connected_users[user_to_remove]
            emit('user_disconnected', {'user_id': user_to_remove}, broadcast=True)
            logger.info(f"User {user_to_remove} disconnected", extra={
                'custom_request_id': request_id
            })
        
        logger.info(f"Client disconnected: {request.sid}", extra={
            'custom_request_id': request_id
        })
    except Exception as e:
        logger.error(f"Error in disconnect handler: {str(e)}")

def handle_join_room(data):
    """Handle user joining a chat room"""
    try:
        request_id = getattr(g, 'request_id', 'unknown')
        
        user_id = data.get('user_id')
        room = data.get('room', 'general')
        username = data.get('username', 'Anonymous')
        
        if not user_id:
            emit('error', {'message': 'User ID is required'})
            return
        
        # Join the room
        join_room(room)
        connected_users[user_id] = request.sid
        
        # Get recent messages for the room
        recent_messages = chat_service.get_recent_messages(room)
        
        # Send recent messages to the user
        emit('recent_messages', {'messages': [msg.dict() for msg in recent_messages]})
        
        # Notify others in the room
        emit('user_joined', {
            'user_id': user_id,
            'username': username,
            'message': f'{username} joined the room'
        }, room=room, include_self=False)
        
        logger.info(f"User {username} joined room {room}", extra={
            'custom_request_id': request_id,
            'custom_user_id': user_id,
            'custom_room': room
        })
        
    except Exception as e:
        logger.error(f"Error in join_room: {str(e)}")
        emit('error', {'message': 'Failed to join room'})

def handle_leave_room(data):
    """Handle user leaving a chat room"""
    try:
        request_id = getattr(g, 'request_id', 'unknown')
        
        user_id = data.get('user_id')
        room = data.get('room', 'general')
        username = data.get('username', 'Anonymous')
        
        if user_id in connected_users:
            leave_room(room)
            emit('user_left', {
                'user_id': user_id,
                'username': username,
                'message': f'{username} left the room'
            }, room=room, include_self=False)
            
            logger.info(f"User {username} left room {room}", extra={
                'custom_request_id': request_id,
                'custom_user_id': user_id,
                'custom_room': room
            })
        
    except Exception as e:
        logger.error(f"Error in leave_room: {str(e)}")
        emit('error', {'message': 'Failed to leave room'})

def handle_send_message(data):
    """Handle sending a chat message"""
    try:
        request_id = getattr(g, 'request_id', 'unknown')
        
        # Validate message data
        if not data.get('message') or not data.get('user_id'):
            emit('error', {'message': 'Message and user_id are required'})
            return
        
        # Create message data
        message_data = ChatMessageCreate(
            message=data.get('message').strip(),
            room=data.get('room', 'general'),
            user_id=data.get('user_id'),
            username=data.get('username')
        )
        
        # Save message to database
        chat_message = chat_service.save_message(message_data)
        
        # Broadcast message to all users in the room
        message_data = {
            'id': chat_message.id,
            'user_id': chat_message.user_id,
            'username': chat_message.username,
            'message': chat_message.message,
            'timestamp': chat_message.timestamp.isoformat(),
            'room': chat_message.room
        }
        
        emit('new_message', message_data, room=chat_message.room)
        
        logger.info(f"Message sent in room {chat_message.room} by {chat_message.username}", extra={
            'custom_request_id': request_id,
            'custom_user_id': chat_message.user_id,
            'custom_room': chat_message.room
        })
        
    except (MessageValidationException, ChatServiceException) as e:
        logger.warning(f"Error sending message: {str(e)}")
        emit('error', {'message': str(e)})
    except Exception as e:
        logger.error(f"Unexpected error sending message: {str(e)}")
        emit('error', {'message': 'Failed to send message'})

def handle_get_message_history(data):
    """Handle request for message history"""
    try:
        request_id = getattr(g, 'request_id', 'unknown')
        
        room = data.get('room', 'general')
        page = data.get('page', 1)
        per_page = data.get('per_page', 20)
        
        history = chat_service.get_message_history(room, page, per_page)
        emit('message_history', history.dict())
        
        logger.info(f"Message history requested for room {room}", extra={
            'custom_request_id': request_id,
            'custom_room': room
        })
        
    except Exception as e:
        logger.error(f"Error getting message history: {str(e)}")
        emit('error', {'message': 'Failed to get message history'})

def handle_typing(data):
    """Handle typing indicator"""
    try:
        request_id = getattr(g, 'request_id', 'unknown')
        
        user_id = data.get('user_id')
        room = data.get('room', 'general')
        is_typing = data.get('is_typing', False)
        username = data.get('username', f'User_{user_id}')
        
        emit('user_typing', {
            'user_id': user_id,
            'username': username,
            'is_typing': is_typing
        }, room=room, include_self=False)
        
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"User {username} typing in room {room}", extra={
                'custom_request_id': request_id,
                'custom_user_id': user_id,
                'custom_room': room
            })
            
    except Exception as e:
        logger.error(f"Error in typing handler: {str(e)}")

def handle_get_connected_users(data):
    """Handle request for connected users"""
    try:
        request_id = getattr(g, 'request_id', 'unknown')
        
        room = data.get('room', 'general')
        
        # Get users in the room (this is a simplified version)
        emit('connected_users', {
            'users': list(connected_users.keys()),
            'count': len(connected_users),
            'room': room
        })
        
        logger.info(f"Connected users requested for room {room}", extra={
            'custom_request_id': request_id,
            'custom_room': room
        })
        
    except Exception as e:
        logger.error(f"Error getting connected users: {str(e)}")
        emit('error', {'message': 'Failed to get connected users'}) 