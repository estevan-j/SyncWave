import uuid
from flask import request, g
from .logger import get_logger

def setup_basic_logging(app):
    """
    Logging básico - Solo request ID y errores
    """
    logger = get_logger("requests")
    
    @app.before_request
    def before_request():
        # Solo generar request_id
        g.request_id = str(uuid.uuid4())[:8]  # ID corto para ahorrar espacio
    
    @app.after_request
    def after_request(response):
        # Solo loggear errores (4xx, 5xx)
        if response.status_code >= 400:
            logger.warning(f"{request.method} {request.path} - {response.status_code}", extra={
                'custom_request_id': getattr(g, 'request_id', 'unknown')
            })
        
        # Agregar request_id al header (útil para debugging)
        response.headers['X-Request-ID'] = getattr(g, 'request_id', 'unknown')
        return response
    
    @app.teardown_request
    def log_errors(exception):
        # Solo loggear excepciones reales
        if exception:
            logger.error(f"Request failed: {str(exception)}", extra={
                'custom_request_id': getattr(g, 'request_id', 'unknown')
            })

# Función simplificada - sin correlation ID para ahorrar recursos
def setup_request_logging(app):
    """Alias para compatibilidad"""
    setup_basic_logging(app)