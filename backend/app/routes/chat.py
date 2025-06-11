from flask import Blueprint, request
from flask_socketio import emit, join_room, leave_room, disconnect
from werkzeug.security import generate_password_hash
from app.services.chat_service import ChatService
from app.models.database import db, User
from app.utils.responses import ApiResponse
import logging

chat_bp = Blueprint('chat', __name__)

# Diccionario para mantener usuarios conectados
connected_users = {}

def handle_connect():
    """Handle client connection"""
    try:
        print(f'✅ Client connected: {request.sid}')
        emit('status', {'msg': f'{request.sid} has connected'})
    except Exception as e:
        print(f'❌ Error in connect handler: {str(e)}')

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
            emit('user_disconnected', {'user_id': user_to_remove}, broadcast=True)
        
        print(f'❌ Client disconnected: {request.sid}')
    except Exception as e:
        print(f'❌ Error in disconnect handler: {str(e)}')

def handle_join_room(data):
    """Handle user joining a chat room"""
    try:
        user_id = data.get('user_id')
        room = data.get('room', 'general')
        username = data.get('username', 'Anonymous')
        
        if not user_id:
            emit('error', {'message': 'User ID is required'})
            return
        
        # Verify user exists or create temporary user for chat
        user = User.query.get(user_id)
        if not user:
            # Create temporary user for monolithic app
            try:
                # Hash the password for security
                hashed_password = generate_password_hash('temp_password')
                
                user = User(
                    id=user_id,
                    email=f'temp_{user_id}@musicapp.com',
                    password=hashed_password,
                    username=username
                )
                db.session.add(user)
                db.session.commit()
                print(f'✅ Created temporary user: {username} (ID: {user_id})')
            except Exception as e:
                print(f'❌ Error creating temporary user: {str(e)}')
                # Continue anyway with basic user info
                user = type('User', (), {'username': username, 'id': user_id})()
        
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
            'username': user.username if hasattr(user, 'username') else username,
            'message': f'{user.username if hasattr(user, "username") else username} joined the room'
        }, room=room, include_self=False)
        
        print(f'👋 User {user.username if hasattr(user, "username") else username} joined room {room}')
        
    except Exception as e:
        print(f'❌ Error in join_room: {str(e)}')
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
        
        # Verify user exists or get from connected users
        user = User.query.get(user_id)
        if not user:
            # For monolithic app, create temporary user for messaging
            username = data.get('username', f'User_{user_id}')
            try:
                hashed_password = generate_password_hash('temp_password')
                
                user = User(
                    id=user_id,
                    email=f'temp_{user_id}@musicapp.com',
                    password=hashed_password,
                    username=username
                )
                db.session.add(user)
                db.session.commit()
                print(f'✅ Created temporary user for message: {username} (ID: {user_id})')
            except Exception as e:
                print(f'❌ Error creating user for message: {str(e)}')
                # Continue with basic user object
                user = type('User', (), {'username': username, 'id': user_id})()
        
        # Save message to database
        chat_message = ChatService.save_message(user_id, message_text, room)
        if not chat_message:
            emit('error', {'message': 'Failed to save message'})
            return
        
        # Broadcast message to all users in the room
        message_data = {
            'id': chat_message.id,
            'user_id': user_id,
            'username': user.username if hasattr(user, 'username') else f'User_{user_id}',
            'message': message_text,
            'timestamp': chat_message.timestamp.isoformat(),
            'room': room
        }
        
        emit('new_message', message_data, room=room)
        print(f'💬 Message sent in room {room} by {user.username if hasattr(user, "username") else f"User_{user_id}"}: {message_text}')
        
    except Exception as e:
        print(f'❌ Error sending message: {str(e)}')
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
        username = user.username if user and hasattr(user, 'username') else f'User_{user_id}'
        
        emit('user_typing', {
            'user_id': user_id,
            'username': username,
            'is_typing': is_typing
        }, room=room, include_self=False)
            
    except Exception as e:
        print(f'❌ Error in typing handler: {str(e)}')

# REST API endpoints for chat
@chat_bp.route('/rooms', methods=['GET'])
def get_active_rooms():
    """Get list of active chat rooms"""
    try:
        rooms = ChatService.get_active_rooms()
        return ApiResponse.success(rooms)
    except Exception as e:
        return ApiResponse.server_error('Failed to get rooms')

@chat_bp.route('/debug', methods=['GET'])
def debug_websocket():
    """Debug endpoint for WebSocket status"""
    try:
        return ApiResponse.success({
            'connected_users': len(connected_users),
            'users': list(connected_users.keys()),
            'socket_rooms': 'Available in runtime only',
            'status': 'WebSocket service running'
        })
    except Exception as e:
        return ApiResponse.server_error('Failed to get debug info')

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
