"""
WebSocket event handlers for chat functionality
"""
from flask import request
from flask_socketio import emit, join_room, leave_room
from app.services.chat_service import ChatService
from app.core.supabase import get_supabase_admin
import logging

logger = logging.getLogger("websocket_controller")

# Diccionario para mantener usuarios conectados
connected_users = {}


def handle_connect():
    """Handle client connection"""
    try:
        logger.info(f'✅ Client connected: {request.sid}')
        emit('status', {'msg': f'{request.sid} has connected'})
    except Exception as e:
        logger.error(f'❌ Error in connect handler: {str(e)}')


def handle_disconnect():
    """Handle client disconnection"""
    try:
        # Remove user from connected users if exists
        user_to_remove = None
        for user_id, session_id in connected_users.items():
            if session_id == request.sid:
                user_to_remove = user_id
                break

        if user_to_remove:
            del connected_users[user_to_remove]
            emit('user_disconnected', {
                'user_id': user_to_remove
            }, broadcast=True)

        logger.info(f'❌ Client disconnected: {request.sid}')
    except Exception as e:
        logger.error(f'❌ Error in disconnect handler: {str(e)}')


def handle_join_room(data):
    """Handle user joining a chat room"""
    try:
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
        chat_service = ChatService()
        recent_messages = chat_service.get_recent_messages(room)

        # Send recent messages to the user
        emit('recent_messages', {'messages': [
             msg.dict() for msg in recent_messages]})

        # Notify others in the room
        emit('user_joined', {
            'user_id': user_id,
            'username': username,
            'message': f'{username} joined the room'
        }, room=room, include_self=False)

        logger.info(f'👋 User {username} joined room {room}')

    except Exception as e:
        logger.error(f'❌ Error in join_room: {str(e)}')
        emit('error', {'message': 'Failed to join room'})


def handle_leave_room(data):
    """Handle user leaving a chat room"""
    try:
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

            logger.info(f'User {username} left room {room}')

    except Exception as e:
        logger.error(f'Error in leave_room: {str(e)}')
        emit('error', {'message': 'Failed to leave room'})


def handle_send_message(data):
    """Handle sending a chat message"""
    try:
        user_id = data.get('user_id')
        message_text = data.get('message', '').strip()
        room = data.get('room', 'general')
        username = data.get('username', f'User_{user_id}')

        if not user_id or not message_text:
            emit('error', {'message': 'User ID and message are required'})
            return

        # Create message data
        from app.schemas.chat_schema import ChatMessageCreate
        message_data = ChatMessageCreate(
            user_id=user_id,
            username=username,
            message=message_text,
            room=room
        )

        # Save message using ChatService
        chat_service = ChatService()
        saved_message = chat_service.save_message(message_data)

        if not saved_message:
            emit('error', {'message': 'Failed to save message'})
            return

        # Broadcast message to all users in the room
        message_data_dict = saved_message.dict()
        emit('new_message', message_data_dict, room=room)
        logger.info(
            f'💬 Message sent in room {room} by {username}: {message_text}')

    except Exception as e:
        logger.error(f'❌ Error sending message: {str(e)}')
        emit('error', {'message': 'Failed to send message'})


def handle_get_message_history(data):
    """Handle request for message history"""
    try:
        room = data.get('room', 'general')
        page = data.get('page', 1)
        per_page = data.get('per_page', 20)

        chat_service = ChatService()
        history = chat_service.get_message_history(room, page, per_page)
        emit('message_history', history.dict())

    except Exception as e:
        logger.error(f'Error getting message history: {str(e)}')
        emit('error', {'message': 'Failed to get message history'})


def handle_typing(data):
    """Handle typing indicator"""
    try:
        user_id = data.get('user_id')
        room = data.get('room', 'general')
        username = data.get('username', f'User_{user_id}')
        is_typing = data.get('is_typing', False)

        emit('user_typing', {
            'user_id': user_id,
            'username': username,
            'is_typing': is_typing
        }, room=room, include_self=False)

    except Exception as e:
        logger.error(f'❌ Error in typing handler: {str(e)}')


def handle_get_connected_users(data):
    """Handle request for connected users"""
    try:
        room = data.get('room', 'general')

        # Get users connected to the specific room
        room_users = []
        for user_id, session_id in connected_users.items():
            # In a real implementation, you'd check which users are in which rooms
            room_users.append({
                'user_id': user_id,
                'session_id': session_id
            })

        emit('connected_users', {
            'room': room,
            'users': room_users,
            'count': len(room_users)
        })

    except Exception as e:
        logger.error(f'❌ Error getting connected users: {str(e)}')
        emit('error', {'message': 'Failed to get connected users'})
