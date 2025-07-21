import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'assets')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SocketIO configuration
    SOCKETIO_ASYNC_MODE = 'eventlet'
    SOCKETIO_CORS_ALLOWED_ORIGINS = [
        'http://localhost:3000',    # React
        'http://localhost:5173',    # Vite
        'http://localhost:8080',    # Vue CLI
        'http://127.0.0.1:3000',
        'http://127.0.0.1:5173',
        'http://127.0.0.1:8080'
    ]


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 'postgresql://user:password@localhost/musicapp')


config = {
    'production': ProductionConfig
}
