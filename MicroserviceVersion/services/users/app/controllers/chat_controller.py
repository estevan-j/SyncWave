from flask import Blueprint, request, jsonify, g
from app.schemas.chat_schema import (
    ChatMessageCreate,
    ChatMessageResponse,
    MessageHistoryResponse,
    JoinRoomRequest,
    LeaveRoomRequest,
    TypingIndicatorRequest,
    DeleteMessageRequest
)
from app.services.chat_service import ChatService
from app.exceptions.chat_exceptions import (
    MessageValidationException,
    MessageNotFoundException,
    UnauthorizedMessageException,
    ChatServiceException
)
import functools
import logging

# Blueprint
chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

# Instancia del servicio
chat_service = ChatService()

# Logger
logger = logging.getLogger("chat_controller")


def handle_chat_response(func):
    """Decorador para manejo de respuestas del chat"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        request_id = getattr(g, 'request_id', 'unknown')
        try:
            result = func(*args, **kwargs)
            return result

        except MessageValidationException as e:
            logger.warning(f"Message validation error in {func.__name__}", extra={
                'custom_request_id': request_id
            })
            return jsonify({
                "error": "Message validation failed",
                "message": str(e),
                "request_id": request_id
            }), 400

        except MessageNotFoundException as e:
            logger.warning(f"Message not found in {func.__name__}", extra={
                'custom_request_id': request_id
            })
            return jsonify({
                "error": "Message not found",
                "message": str(e),
                "request_id": request_id
            }), 404

        except UnauthorizedMessageException as e:
            logger.warning(f"Unauthorized action in {func.__name__}", extra={
                'custom_request_id': request_id
            })
            return jsonify({
                "error": "Unauthorized",
                "message": str(e),
                "request_id": request_id
            }), 403

        except ChatServiceException as e:
            logger.error(f"Chat service error in {func.__name__}: {str(e)}", extra={
                'custom_request_id': request_id
            })
            return jsonify({
                "error": "Chat service error",
                "message": str(e),
                "request_id": request_id
            }), 500

        except ValueError as e:
            logger.error(f"Validation error in {func.__name__}: {str(e)}", extra={
                'custom_request_id': request_id
            })
            return jsonify({
                "error": "Invalid input data",
                "message": str(e),
                "request_id": request_id
            }), 400

        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}", extra={
                'custom_request_id': request_id
            })
            return jsonify({
                "error": "Internal server error",
                "message": str(e),
                "request_id": request_id
            }), 500

    return wrapper


@chat_bp.route('/messages', methods=['POST'])
@handle_chat_response
def send_message():
    """Send a new chat message"""
    request_id = getattr(g, 'request_id', 'unknown')

    data = request.get_json()
    if not data:
        return jsonify({
            "error": "No JSON data provided",
            "request_id": request_id
        }), 400

    try:
        message_data = ChatMessageCreate(**data)
    except Exception as e:
        raise ValueError(f"Invalid message data: {str(e)}")

    # Save message
    message_response = chat_service.save_message(message_data)

    if logger.isEnabledFor(logging.INFO):
        logger.info("Message sent", extra={
            'custom_request_id': request_id,
            'custom_room': message_data.room,
            'custom_user_id': message_data.user_id
        })

    return jsonify({
        **message_response.dict(),
        "request_id": request_id
    }), 201


@chat_bp.route('/messages', methods=['GET'])
@handle_chat_response
def get_messages():
    """Get recent messages for a room"""
    request_id = getattr(g, 'request_id', 'unknown')

    room = request.args.get('room', 'general')
    limit = request.args.get('limit', 50, type=int)

    if limit > 100:
        limit = 100  # Cap at 100 messages

    messages = chat_service.get_recent_messages(room, limit)

    return jsonify({
        "messages": [msg.dict() for msg in messages],
        "room": room,
        "count": len(messages),
        "request_id": request_id
    }), 200


@chat_bp.route('/messages/history', methods=['GET'])
@handle_chat_response
def get_message_history():
    """Get paginated message history"""
    request_id = getattr(g, 'request_id', 'unknown')

    room = request.args.get('room', 'general')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    if per_page > 50:
        per_page = 50  # Cap at 50 messages per page

    history = chat_service.get_message_history(room, page, per_page)

    return jsonify({
        **history.dict(),
        "request_id": request_id
    }), 200


@chat_bp.route('/messages/<int:message_id>', methods=['DELETE'])
@handle_chat_response
def delete_message(message_id):
    """Delete a message"""
    request_id = getattr(g, 'request_id', 'unknown')

    data = request.get_json()
    if not data:
        return jsonify({
            "error": "No JSON data provided",
            "request_id": request_id
        }), 400

    try:
        delete_request = DeleteMessageRequest(**data)
    except Exception as e:
        raise ValueError(f"Invalid delete request data: {str(e)}")

    success = chat_service.delete_message(message_id, delete_request.user_id)

    if success:
        if logger.isEnabledFor(logging.INFO):
            logger.info("Message deleted", extra={
                'custom_request_id': request_id,
                'custom_message_id': message_id,
                'custom_user_id': delete_request.user_id
            })

        return jsonify({
            "message": "Message deleted successfully",
            "request_id": request_id
        }), 200
    else:
        return jsonify({
            "error": "Failed to delete message",
            "request_id": request_id
        }), 400


@chat_bp.route('/rooms', methods=['GET'])
@handle_chat_response
def get_active_rooms():
    """Get list of active chat rooms"""
    request_id = getattr(g, 'request_id', 'unknown')

    rooms = chat_service.get_active_rooms()

    return jsonify({
        "rooms": rooms,
        "count": len(rooms),
        "request_id": request_id
    }), 200


@chat_bp.route('/rooms/<room_name>/statistics', methods=['GET'])
@handle_chat_response
def get_room_statistics(room_name):
    """Get statistics for a specific room"""
    request_id = getattr(g, 'request_id', 'unknown')

    stats = chat_service.get_room_statistics(room_name)

    return jsonify({
        **stats,
        "request_id": request_id
    }), 200


@chat_bp.route('/debug', methods=['GET'])
@handle_chat_response
def debug_chat():
    """Debug endpoint for chat service status"""
    request_id = getattr(g, 'request_id', 'unknown')

    # Get basic statistics
    rooms = chat_service.get_active_rooms()
    general_stats = chat_service.get_room_statistics('general')

    return jsonify({
        "status": "Chat service running",
        "active_rooms": len(rooms),
        "rooms": rooms,
        "general_room_stats": general_stats,
        "request_id": request_id
    }), 200
