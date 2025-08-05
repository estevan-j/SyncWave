import os
from flask import jsonify

def setup_basic_health(app):
    """Health check mínimo"""
    
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'ok',
            'service': os.getenv('SERVICE_NAME', 'unknown')
        }), 200
    
    @app.route('/metrics')
    def metrics():
        """Endpoint básico para Prometheus"""
        from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
        from flask import Response
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)