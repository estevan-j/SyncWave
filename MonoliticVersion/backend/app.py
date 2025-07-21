from flask import Flask, jsonify, send_file
from flask_cors import CORS
from flask_socketio import SocketIO
from dotenv import load_dotenv
import os
from app.routes.users import users_bp
from app.routes.music import music_bp
from app.routes.favorites import favorites_bp
from app.routes.chat import chat_bp
from app.models.database import db
# Load environment variables
load_dotenv()


def create_app():
    static_folder = os.path.join(os.path.dirname(
        __file__), 'app', 'static', 'browser')
    app = Flask(__name__, static_folder=static_folder, static_url_path='')

    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'assets')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)    # Enable CORS for frontend consumption
    CORS(app, origins=[
        'http://localhost:5000',    # Backend/Frontend monolítico
        'http://127.0.0.1:5000',
        'http://localhost:4200',
        'http://localhost:3000',    # Para desarrollo con frontend separado
        'http://127.0.0.1:3000',
        'http://127.0.0.1:4200',
        'http://127.0.0.1:5173',
        'http://127.0.0.1:57313',
        'http://127.0.0.1:8080'
    ])    # Initialize SocketIO with simplified configuration
    socketio = SocketIO(app,
                        cors_allowed_origins="*",
                        async_mode='threading',
                        logger=True,
                        engineio_logger=False,
                        transports=['polling'],
                        ping_timeout=60,
                        ping_interval=25
                        )

    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(music_bp, url_prefix='/api/music')
    app.register_blueprint(favorites_bp, url_prefix='/api/favorites')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')

    # Register SocketIO events
    from app.routes.chat import (
        handle_connect, handle_disconnect, handle_join_room,
        handle_leave_room, handle_send_message, handle_get_message_history,
        handle_typing
    )

    socketio.on_event('connect', handle_connect)
    socketio.on_event('disconnect', handle_disconnect)
    socketio.on_event('join_room', handle_join_room)
    socketio.on_event('leave_room', handle_leave_room)
    socketio.on_event('send_message', handle_send_message)
    socketio.on_event('get_message_history', handle_get_message_history)
    socketio.on_event('typing', handle_typing)

    # Create database tables
    with app.app_context():
        db.create_all()

    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'Music App Backend',
            'version': '1.0.0',
            'features': ['REST API', 'WebSocket Chat', 'SQLAlchemy Database']
        })

    # Root endpoint - servir index.html de Angular
    @app.route('/')
    def root():
        try:
            return send_file(os.path.join(app.static_folder, 'index.html'))
        except (FileNotFoundError, TypeError, AttributeError):
            return jsonify({
                'message': 'Frontend not built yet. Run "ng build" in fronted folder.',
                'status': 'warning',
                'build_command': 'cd fronted && npm run build',
                'static_folder': app.static_folder
            })    # Serve uploaded files

    @app.route('/assets/<path:filename>')
    def serve_assets(filename):
        """Serve uploaded music files from assets folder"""
        try:
            # Construir la ruta absoluta a la carpeta assets
            upload_folder = app.config['UPLOAD_FOLDER']
            if not os.path.isabs(upload_folder):
                # Si es una ruta relativa, hacerla relativa al directorio del backend
                upload_path = os.path.join(
                    os.path.dirname(__file__), upload_folder)
            else:
                upload_path = upload_folder

            file_path = os.path.join(upload_path, filename)

            # Verificar que el archivo existe
            if not os.path.exists(file_path):
                return jsonify({
                    'success': False,
                    'message': f'Asset file not found: {filename}',
                    'error_code': 'ASSET_FILE_NOT_FOUND'
                }), 404

            return send_file(file_path)
        except FileNotFoundError:
            return jsonify({
                'success': False,
                'message': f'Asset file not found: {filename}',
                'error_code': 'ASSET_FILE_NOT_FOUND'
            }), 404
        except Exception as e:
            print(f"Error serving asset file {filename}: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error serving asset file',
                'error_code': 'ASSET_SERVE_ERROR'
            }), 500

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': 'Resource not found',
            'error_code': 'NOT_FOUND'
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error_code': 'SERVER_ERROR'
        }), 500

    @app.errorhandler(413)
    def file_too_large(error):
        return jsonify({
            'success': False,
            'message': 'File too large. Maximum size is 16MB',
            'error_code': 'FILE_TOO_LARGE'
        }), 413

    return app, socketio


if __name__ == '__main__':
    app, socketio = create_app()
    port = int(os.getenv('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
