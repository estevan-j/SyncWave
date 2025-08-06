"""
Users Authentication Microservice - Configuración básica optimizada
"""
from flask import Flask, jsonify, g
from flask_cors import CORS
from flask_socketio import SocketIO
from app.config import get_config
from app.controllers.auth_controller import auth_bp

import logging

# Configurar logging básico
logging.basicConfig(level=logging.INFO)

# Logger principal - solo para errores importantes
app_logger = logging.getLogger("users-auth-app")


def create_app(config_name=None):
    """Create and configure the Flask application instance"""

    app = Flask(__name__)

    # Cargar configuración
    config = get_config()
    app.config.from_object(config)
    config.init_app(app)

    # ✅ Solo logging básico - sin correlation ID para ahorrar recursos
    # setup_request_logging(app)  # Removed custom logging setup

    # Configurar CORS básico
    CORS(app,
         origins=app.config.get('CORS_ORIGINS', ['*']),
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'])

    # Initialize SocketIO for WebSocket support
    socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

    # Registrar blueprints
    from app.controllers.auth_controller import auth_bp
    from app.controllers.chat_controller import chat_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)

    # Register WebSocket event handlers
    from app.controllers.websocket_controller import (
        handle_connect, handle_disconnect, handle_join_room, handle_leave_room,
        handle_send_message, handle_get_message_history, handle_typing, handle_get_connected_users
    )
    
    socketio.on_event('connect', handle_connect)
    socketio.on_event('disconnect', handle_disconnect)
    socketio.on_event('join_room', handle_join_room)
    socketio.on_event('leave_room', handle_leave_room)
    socketio.on_event('send_message', handle_send_message)
    socketio.on_event('get_message_history', handle_get_message_history)
    socketio.on_event('typing', handle_typing)
    socketio.on_event('get_connected_users', handle_get_connected_users)

    # ✅ Error handlers simplificados
    setup_basic_error_handlers(app)

    # ✅ Health check básico
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'ok',
            'service': app.config.get('SERVICE_NAME', 'users-auth'),
            'version': app.config.get('SERVICE_VERSION', '1.0.0')
        }), 200

    return app


def setup_basic_error_handlers(app):
    """Error handlers básicos para práctica"""

    error_logger = logging.getLogger("error_handler")

    @app.errorhandler(400)
    def bad_request(error):
        request_id = getattr(g, 'request_id', 'unknown')
        error_logger.warning(f"Bad request: {str(error)}", extra={
            'custom_request_id': request_id
        })
        return jsonify({
            'error': 'Bad request',
            'message': str(error),
            'request_id': request_id
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        request_id = getattr(g, 'request_id', 'unknown')
        error_logger.warning(f"Unauthorized: {str(error)}", extra={
            'custom_request_id': request_id
        })
        return jsonify({
            'error': 'Unauthorized',
            'message': str(error),
            'request_id': request_id
        }), 401

    @app.errorhandler(404)
    def not_found(error):
        request_id = getattr(g, 'request_id', 'unknown')
        return jsonify({
            'error': 'Not found',
            'message': str(error),
            'request_id': request_id
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        request_id = getattr(g, 'request_id', 'unknown')
        error_logger.error(f"Internal error: {str(error)}", extra={
            'custom_request_id': request_id
        })
        return jsonify({
            'error': 'Internal server error',
            'message': str(error),
            'request_id': request_id
        }), 500