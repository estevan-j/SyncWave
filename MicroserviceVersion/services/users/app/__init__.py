"""
Users Authentication Microservice - Configuración básica optimizada
"""
from flask import Flask, jsonify, g, request, make_response
from flask_cors import CORS
from flask_socketio import SocketIO
from app.config import get_config

import logging

# Configurar logging básico
logging.basicConfig(level=logging.INFO)

# Logger principal - solo para errores importantes
app_logger = logging.getLogger("users-auth-app")

# Variable global para SocketIO
socketio = SocketIO()


def create_app(config_name=None):
    """Create and configure the Flask application instance"""

    app = Flask(__name__)

    # Cargar configuración
    config = get_config()
    app.config.from_object(config)
    config.init_app(app)

    # CORS origins
    cors_origins = [
        'http://localhost:4200',
        'http://localhost:8090',  
        'http://syncwave-frontend:4200',
        'http://syncwave-api-gateway:8080',
        'http://syncwave-nginx:80'
    ]

    # ✅ Configuración CORS completa y robusta
    from flask_cors import CORS
    CORS(app, 
         origins=cors_origins,
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
         supports_credentials=True,
         max_age=3600  # Cache preflight por 1 hora
    )

    # ✅ Handler adicional para asegurar OPTIONS
    @app.before_request
    def handle_options():
        if request.method == 'OPTIONS':
            origin = request.headers.get('Origin')
            if origin in cors_origins:
                response = app.make_default_options_response()
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,X-Requested-With'
                response.headers['Access-Control-Allow-Credentials'] = 'true'
                response.headers['Access-Control-Max-Age'] = '3600'
                return response

    # ✅ Asegurar CORS en todas las respuestas
    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')
        if origin in cors_origins:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response

    # Configurar SocketIO
    socketio.init_app(app,
                      cors_allowed_origins=cors_origins,
                      logger=False,
                      engineio_logger=False)

    # ...resto del código...

    
    # Inicializar middleware de métricas
    from app.metrics_middleware import metrics_middleware
    metrics_middleware.init_app(app)

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
