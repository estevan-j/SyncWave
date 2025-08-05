import os
from prometheus_client import Counter, Histogram
from flask import request, g

# Solo métricas básicas
REQUEST_COUNT = Counter(
    'requests_total',
    'Total requests',
    ['service', 'method', 'status_code']
)

ERROR_COUNT = Counter(
    'errors_total',
    'Total errors',
    ['service', 'error_type']
)

def setup_basic_metrics(app):
    """
    Métricas básicas - mínimo overhead
    """
    service_name = os.getenv('SERVICE_NAME', 'unknown')
    
    @app.after_request
    def count_requests(response):
        # Solo contar requests y errores
        REQUEST_COUNT.labels(
            service=service_name,
            method=request.method,
            status_code=str(response.status_code)
        ).inc()
        
        # Contar errores por separado
        if response.status_code >= 400:
            error_type = 'client_error' if response.status_code < 500 else 'server_error'
            ERROR_COUNT.labels(
                service=service_name,
                error_type=error_type
            ).inc()
        
        return response

# Solo funciones esenciales
def request_count():
    return REQUEST_COUNT

def error_count():
    return ERROR_COUNT