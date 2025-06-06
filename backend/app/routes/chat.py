from flask import Blueprint, request
from flask_socketio import emit, join_room, leave_room, disconnect
from app.services.chat_service import ChatService
from app.models.database import db, User
from app.utils.responses import ApiResponse
import logging

chat_bp = Blueprint('chat', __name__)

# Diccionario para mantener usuarios conectados
connected_users = {}

def handle_connect():
    """Handle client connection"""
    print(f'Client connected: {request.sid}')
    emit('status', {'msg': f'{request.sid} has connected'})

def handle_disconnect():
    """Handle client disconnection"""
    # Remove user from connected users if exists
    user_to_remove = None
    for user_id, session_id in connected_users.items():
        if session_id == request.sid:
            user_to_remove = user_id
            break
    
    if user_to_remove:
        del connected_users[user_to_remove]
        emit('user_disconnected', {'user_id': user_to_remove}, broadcast=True)
    
    print(f'Client disconnected: {request.sid}')

def handle_join_room(data):
    """Handle user joining a chat room"""
    try:
        user_id = data.get('user_id')
        room = data.get('room', 'general')
        username = data.get('username', 'Anonymous')
        
        if not user_id:
            emit('error', {'message': 'User ID is required'})
            return
        
        # Verify user exists
        user = User.query.get(user_id)
        if not user:
            emit('error', {'message': 'User not found'})
            return
        
        # Join the room
        join_room(room)
        connected_users[user_id] = request.sid
        
        # Get recent messages for the room
        recent_messages = ChatService.get_recent_messages(room)
        
        # Send recent messages to the user
        emit('recent_messages', {'messages': recent_messages})
        
        # Notify others in the room
        emit('user_joined', {
            'user_id': user_id,
            'username': user.username,
            'message': f'{user.username} joined the room'
        }, room=room, include_self=False)
        
        print(f'User {user.username} joined room {room}')
        
    except Exception as e:
        print(f'Error in join_room: {str(e)}')
        emit('error', {'message': 'Failed to join room'})

def handle_leave_room(data):
    """Handle user leaving a chat room"""
    try:
        user_id = data.get('user_id')
        room = data.get('room', 'general')
        
        if user_id in connected_users:
            user = User.query.get(user_id)
            if user:
                leave_room(room)
                emit('user_left', {
                    'user_id': user_id,
                    'username': user.username,
                    'message': f'{user.username} left the room'
                }, room=room, include_self=False)
                
                print(f'User {user.username} left room {room}')
        
    except Exception as e:
        print(f'Error in leave_room: {str(e)}')
        emit('error', {'message': 'Failed to leave room'})

def handle_send_message(data):
    """Handle sending a chat message"""
    try:
        # Validate message data
        errors = ChatService.validate_message_data(data)
        if errors:
            emit('error', {'message': '; '.join(errors)})
            return
        
        user_id = data.get('user_id')
        message_text = data.get('message').strip()
        room = data.get('room', 'general')
        
        # Verify user exists
        user = User.query.get(user_id)
        if not user:
            emit('error', {'message': 'User not found'})
            return
        
        # Save message to database
        chat_message = ChatService.save_message(user_id, message_text, room)
        if not chat_message:
            emit('error', {'message': 'Failed to save message'})
            return
        
        # Broadcast message to all users in the room
        message_data = {
            'id': chat_message.id,
            'user_id': user_id,
            'username': user.username,
            'message': message_text,
            'timestamp': chat_message.timestamp.isoformat(),
            'room': room
        }
        
        emit('new_message', message_data, room=room)
        print(f'Message sent in room {room} by {user.username}: {message_text}')
        
    except Exception as e:
        print(f'Error sending message: {str(e)}')
        emit('error', {'message': 'Failed to send message'})

def handle_get_message_history(data):
    """Handle request for message history"""
    try:
        room = data.get('room', 'general')
        page = data.get('page', 1)
        per_page = data.get('per_page', 20)
        
        history = ChatService.get_message_history(room, page, per_page)
        emit('message_history', history)
        
    except Exception as e:
        print(f'Error getting message history: {str(e)}')
        emit('error', {'message': 'Failed to get message history'})

def handle_typing(data):
    """Handle typing indicator"""
    try:
        user_id = data.get('user_id')
        room = data.get('room', 'general')
        is_typing = data.get('is_typing', False)
        
        user = User.query.get(user_id)
        if user:
            emit('user_typing', {
                'user_id': user_id,
                'username': user.username,
                'is_typing': is_typing
            }, room=room, include_self=False)
            
    except Exception as e:
        print(f'Error in typing handler: {str(e)}')

# REST API endpoints for chat
@chat_bp.route('/rooms', methods=['GET'])
def get_active_rooms():
    """Get list of active chat rooms"""
    try:
        rooms = ChatService.get_active_rooms()
        return ApiResponse.success(rooms)
    except Exception as e:
        return ApiResponse.server_error('Failed to get rooms')

@chat_bp.route('/rooms/<room>/messages', methods=['GET'])
def get_room_messages(room):
    """Get messages for a specific room"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        history = ChatService.get_message_history(room, page, per_page)
        return ApiResponse.success(history)
    except Exception as e:
        return ApiResponse.server_error('Failed to get messages')

@chat_bp.route('/messages/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    """Delete a message"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return ApiResponse.validation_error('User ID is required')
        
        success = ChatService.delete_message(message_id, user_id)
        if success:
            return ApiResponse.success(None, 'Message deleted successfully')
        else:
            return ApiResponse.error('Message not found or unauthorized', 404)
    except Exception as e:
        return ApiResponse.server_error('Failed to delete message')
