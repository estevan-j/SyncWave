from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import time
import psutil
import os
from flask import request, Response

# =============================================================================
# MÉTRICAS PARA USERS SERVICE
# =============================================================================

# Métricas HTTP básicas
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

# Métricas de negocio específicas para Users
user_registrations_total = Counter(
    'user_registrations_total',
    'Total user registrations',
    ['status']  # success, failed
)

login_attempts_total = Counter(
    'login_attempts_total',
    'Total login attempts',
    ['status', 'method']  # success/failed, email/username
)

jwt_tokens_issued_total = Counter(
    'jwt_tokens_issued_total',
    'Total JWT tokens issued'
)

password_reset_requests_total = Counter(
    'password_reset_requests_total',
    'Total password reset requests',
    ['status']
)

active_sessions_gauge = Gauge(
    'active_sessions_total',
    'Current active user sessions'
)

# Métricas de sistema
memory_usage_bytes = Gauge(
    'nodejs_memory_usage_bytes',
    'Memory usage in bytes',
    ['type']
)

cpu_usage_percent = Gauge(
    'nodejs_cpu_usage_percent',
    'CPU usage percentage'
)

database_connections_active = Gauge(
    'database_connections_active',
    'Active database connections'
)

# =============================================================================
# MIDDLEWARE CLASS
# =============================================================================

class MetricsMiddleware:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        
        # Registrar endpoint de métricas
        app.add_url_rule('/metrics', 'metrics', self.metrics_endpoint, methods=['GET'])
        
        # Inicializar métricas de sistema
        self._update_system_metrics()
    
    def before_request(self):
        request.start_time = time.time()
    
    def after_request(self, response):
        if request.endpoint == 'metrics':
            return response
            
        # Calcular duración
        duration = time.time() - getattr(request, 'start_time', time.time())
        
        # Obtener endpoint (sin parámetros)
        endpoint = request.endpoint or request.path
        
        # Registrar métricas
        http_requests_total.labels(
            method=request.method,
            endpoint=endpoint,
            status=response.status_code
        ).inc()
        
        http_request_duration_seconds.labels(
            method=request.method,
            endpoint=endpoint
        ).observe(duration)
        
        # Actualizar métricas de sistema periódicamente
        self._update_system_metrics()
        
        return response
    
    def metrics_endpoint(self):
        """Endpoint que expone las métricas en formato Prometheus"""
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
    
    def _update_system_metrics(self):
        """Actualizar métricas de sistema"""
        try:
            # Memoria
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            memory_usage_bytes.labels(type='rss').set(memory_info.rss)
            memory_usage_bytes.labels(type='vms').set(memory_info.vms)
            
            # CPU
            cpu_percent = process.cpu_percent()
            cpu_usage_percent.set(cpu_percent)
            
        except Exception as e:
            print(f"Error updating system metrics: {e}")

# =============================================================================
# FUNCIONES UTILITARIAS PARA MÉTRICAS DE NEGOCIO
# =============================================================================

def record_user_registration(success=True):
    """Registrar un intento de registro de usuario"""
    status = 'success' if success else 'failed'
    user_registrations_total.labels(status=status).inc()

def record_login_attempt(success=True, method='email'):
    """Registrar un intento de login"""
    status = 'success' if success else 'failed'
    login_attempts_total.labels(status=status, method=method).inc()

def record_jwt_token_issued():
    """Registrar emisión de token JWT"""
    jwt_tokens_issued_total.inc()

def record_password_reset_request(success=True):
    """Registrar solicitud de reset de contraseña"""
    status = 'success' if success else 'failed'
    password_reset_requests_total.labels(status=status).inc()

def update_active_sessions(count):
    """Actualizar número de sesiones activas"""
    active_sessions_gauge.set(count)

def update_database_connections(count):
    """Actualizar número de conexiones de BD activas"""
    database_connections_active.set(count)

# =============================================================================
# INSTANCIA SINGLETON
# =============================================================================

metrics_middleware = MetricsMiddleware()

# Exportar todo lo necesario
__all__ = [
    'MetricsMiddleware',
    'metrics_middleware',
    'record_user_registration',
    'record_login_attempt',
    'record_jwt_token_issued',
    'record_password_reset_request',
    'update_active_sessions',
    'update_database_connections'
]