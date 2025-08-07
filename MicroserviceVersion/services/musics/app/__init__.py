"""
Music Microservice - Configuración básica optimizada
"""
from flask import Flask, jsonify, g, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from app.config import get_config
from app.extensions import db
from app.controllers.music_controller import music_bp
import os
import logging
import uuid


# Configurar logging básico
logging.basicConfig(level=logging.INFO)
app_logger = logging.getLogger("musics-app")

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
    @app.before_request
    def before_request():
        g.request_id = str(uuid.uuid4())

    # Configurar CORS SIMPLE Y DIRECTO

    # Configurar CORS SIMPLE Y DIRECTO
    CORS(app,
         origins=[
             "http://localhost:8090",
             "http://localhost:4200",
             "http://syncwave-frontend:4200",
             "http://syncwave-api-gateway:8080",
             "http://syncwave-nginx:80"
         ],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
         supports_credentials=True
    )

    # Manejar OPTIONS antes de cualquier cosa
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = jsonify({'status': 'OK'})
            response.headers.add("Access-Control-Allow-Origin", "http://localhost:4200")
            response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization")
            response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS")
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            return response

    # Inicializar middleware de métricas
    from app.metrics_middleware import metrics_middleware
    metrics_middleware.init_app(app)

    # Registrar blueprints
    app.register_blueprint(music_bp)

    # Add route to serve uploaded files
    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        uploads_dir = os.path.join(os.getcwd(), 'uploads')
        return send_from_directory(uploads_dir, filename)

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
    error_logger = logging.getLogger("error_handler")

    @app.errorhandler(400)
    def bad_request(error):
        request_id = getattr(g, 'request_id', 'unknown')
        error_logger.warning(f"Bad request: {str(error)}")
        return jsonify({
            'error': 'Bad request',
            'message': str(error),
            'request_id': request_id
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        request_id = getattr(g, 'request_id', 'unknown')
        error_logger.warning(f"Unauthorized: {str(error)}")
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
        error_logger.error(f"Internal error: {str(error)}")
        db.session.rollback()
        return jsonify({
            'error': 'Internal server error',
            'message': str(error),
            'request_id': request_id
        }), 500