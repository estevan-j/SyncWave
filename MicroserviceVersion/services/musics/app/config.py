"""
Configuration settings for Music microservice
"""
import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production') 
    SQLALCHEMY_TRACK_MODIFICATIONS = False
        # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL')
    SUPABASE_JWT_SECRET = os.getenv('SUPABASE_JWT_SECRET')
    
    # ✅ Configuración de logging simplificada
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'WARNING')  # WARNING por defecto para práctica
    LOG_FORMAT = os.getenv('LOG_FORMAT', 'simple')  # Formato simple por defecto
    SERVICE_NAME = os.getenv('SERVICE_NAME', 'users-auth')
    SERVICE_VERSION = os.getenv('SERVICE_VERSION', '1.0.0')
    
    # CORS Configuration
    CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:5000']
    
    # Error Handling
    PROPAGATE_EXCEPTIONS = True
    
    @staticmethod
    def init_app(app):
        """Inicializar configuración específica de la app"""
        # ✅ Usar la librería compartida
        from microservice_logging import configure_root_logger
        configure_root_logger()

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') 
    SQLALCHEMY_ECHO = True  # Log SQL queries in development

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://user:password@localhost:5432/music_app_musics_prod'
    SQLALCHEMY_ECHO = False


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    return config[os.environ.get('FLASK_ENV', 'development')]
