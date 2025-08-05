import os
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from flask import Response

def setup_prometheus_endpoint(app):
    """
    Configurar endpoint para métricas de Prometheus
    
    Args:
        app: Instancia de Flask
    """
    
    @app.route('/metrics')
    def metrics():
        """Endpoint para que Prometheus scrape las métricas"""
        return Response(
            generate_latest(),
            mimetype=CONTENT_TYPE_LATEST
        )
    
    # Opcional: Endpoint de info del servicio
    @app.route('/info')
    def service_info():
        """Información básica del servicio"""
        return {
            'service': os.getenv('SERVICE_NAME', 'unknown-service'),
            'version': os.getenv('SERVICE_VERSION', '1.0.0'),
            'environment': os.getenv('FLASK_ENV', 'development'),
            'metrics_endpoint': '/metrics'
        }