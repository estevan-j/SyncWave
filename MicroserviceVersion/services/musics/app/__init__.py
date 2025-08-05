"""
Music Microservice - Configuración básica optimizada
"""
from flask import Flask, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from app.config import get_config
from app.extensions import db
from microservice_logging import get_logger, configure_root_logger, setup_request_logging
from app.controllers.music_controller import music_bp


# Configurar logging básico
configure_root_logger()
app_logger = get_logger("musics-app")

def create_app(config_name=None):
    """Create and configure the Flask application instance"""
    app = Flask(__name__)

    # Cargar configuración
    config = get_config()
    app.config.from_object(config)
    config.init_app(app)

    # Inicializar extensiones
    db.init_app(app)

    # Logging de request básico
    setup_request_logging(app)

    # Configurar CORS básico
    CORS(app,
         origins=app.config.get('CORS_ORIGINS', ['*']),
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'])

    # Registrar blueprints (descomenta y ajusta cuando tengas blueprints)
    # from app.controllers.music_controller import music_bp
    app.register_blueprint(music_bp)

    # Error handlers simplificados
    setup_basic_error_handlers(app)

    # Health check básico
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'ok',
            'service': app.config.get('SERVICE_NAME', 'musics'),
            'version': app.config.get('SERVICE_VERSION', '1.0.0')
        }), 200

    # Health check de base de datos
    @app.route('/health/db', methods=['GET'])
    def db_health_check():
        try:
            db.session.execute('SELECT 1')
            return jsonify({'database': 'healthy'}), 200
        except Exception as e:
            return jsonify({'database': 'unhealthy', 'error': str(e)}), 500

    return app

def setup_basic_error_handlers(app):
    """Error handlers básicos para práctica"""
    error_logger = get_logger("error_handler")

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
        db.session.rollback()
        return jsonify({
            'error': 'Internal server error',
            'message': str(error),
            'request_id': request_id}), 500