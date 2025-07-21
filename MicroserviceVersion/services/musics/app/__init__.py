"""
Music Microservice
Flask application factory pattern for music management
"""

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
import os
import logging
import requests
from datetime import timedelta

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    from app.config import config
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # CORS configuration
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Setup logging
    setup_logging(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Create upload folder if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy', 
            'service': 'musics',
            'version': '1.0.0',
            'port': 5002
        }), 200
    
    # Database check endpoint
    @app.route('/health/db')
    def db_health_check():
        try:
            # Simple database query
            db.session.execute('SELECT 1')
            return jsonify({'database': 'healthy'}), 200
        except Exception as e:
            return jsonify({'database': 'unhealthy', 'error': str(e)}), 500
    
    # Service dependency check
    @app.route('/health/dependencies')
    def dependencies_health_check():
        dependencies = {}
        
        # Check User Auth Service
        try:
            response = requests.get(f"{app.config['USER_AUTH_SERVICE_URL']}/health", timeout=5)
            dependencies['user_auth'] = 'healthy' if response.status_code == 200 else 'unhealthy'
        except:
            dependencies['user_auth'] = 'unhealthy'
        
        # Check Chat Service
        try:
            response = requests.get(f"{app.config['CHAT_SERVICE_URL']}/health", timeout=5)
            dependencies['chat'] = 'healthy' if response.status_code == 200 else 'unhealthy'
        except:
            dependencies['chat'] = 'unhealthy'
        
        return jsonify({'dependencies': dependencies}), 200
    
    return app

def setup_logging(app):
    """Setup logging configuration"""
    if not app.debug and not app.testing:
        if app.config['LOG_LEVEL']:
            logging.basicConfig(level=getattr(logging, app.config['LOG_LEVEL']))
        
        # Add file handler for production
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = logging.FileHandler('logs/musics.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Music service startup')

def register_error_handlers(app):
    """Register error handlers for the application"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad Request',
            'message': 'The request was invalid or cannot be served',
            'status_code': 400
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication is required',
            'status_code': 401
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'error': 'Forbidden',
            'message': 'Access is denied',
            'status_code': 403
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found',
            'status_code': 404
        }), 404
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({
            'error': 'Request Entity Too Large',
            'message': 'The file is too large',
            'status_code': 413
        }), 413
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            'error': 'Unprocessable Entity',
            'message': 'The request was well-formed but contains semantic errors',
            'status_code': 422
        }), 422
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred',
            'status_code': 500
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f'Unhandled exception: {str(e)}')
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred',
            'status_code': 500
        }), 500

def register_blueprints(app):
    """Register application blueprints"""
    # Import blueprints here to avoid circular imports
    # Note: Controllers will be implemented later
    pass
    
    # Example of how blueprints will be registered:
    # from app.controllers.music_controller import music_bp
    # app.register_blueprint(music_bp, url_prefix='/api/music')
