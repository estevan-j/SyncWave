from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import time
import psutil
import os
from flask import request, Response

# =============================================================================
# MÉTRICAS PARA MUSIC SERVICE
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

# Métricas de negocio específicas para Music
music_uploads_total = Counter(
    'music_uploads_total',
    'Total music file uploads',
    ['status', 'format']  # success/failed, mp3/wav/etc
)

music_downloads_total = Counter(
    'music_downloads_total',
    'Total music downloads/plays',
    ['format']
)

music_storage_bytes_used = Gauge(
    'music_storage_bytes_used',
    'Storage space used for music files'
)

audio_processing_duration_seconds = Histogram(
    'audio_processing_duration_seconds',
    'Time spent processing audio files',
    ['operation']  # upload, transcode, metadata_extract
)

music_files_total = Gauge(
    'music_files_total',
    'Total number of music files'
)

failed_uploads_total = Counter(
    'failed_uploads_total',
    'Total failed upload attempts',
    ['reason']  # file_too_large, invalid_format, storage_error
)

# Métricas de Supabase
supabase_api_requests_total = Counter(
    'supabase_api_requests_total',
    'Total Supabase API requests',
    ['operation', 'status']  # upload/download/delete, success/error
)

file_upload_size_bytes = Histogram(
    'file_upload_size_bytes',
    'Size of uploaded files in bytes'
)

# Métricas de sistema
memory_usage_bytes = Gauge(
    'nodejs_memory_usage_bytes',
    'Memory usage in bytes',
    ['type']
)

database_queries_duration_seconds = Histogram(
    'database_queries_duration_seconds',
    'Database query duration',
    ['operation']  # select, insert, update, delete
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
        
        # Actualizar métricas de sistema
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
            
        except Exception as e:
            print(f"Error updating system metrics: {e}")

# =============================================================================
# FUNCIONES UTILITARIAS PARA MÉTRICAS DE NEGOCIO
# =============================================================================

def record_music_upload(success=True, file_format='unknown', file_size_bytes=0):
    """Registrar subida de archivo de música"""
    status = 'success' if success else 'failed'
    music_uploads_total.labels(status=status, format=file_format).inc()
    
    if success and file_size_bytes > 0:
        file_upload_size_bytes.observe(file_size_bytes)

def record_music_download(file_format='unknown'):
    """Registrar descarga/reproducción de música"""
    music_downloads_total.labels(format=file_format).inc()

def record_audio_processing_time(duration, operation='upload'):
    """Registrar tiempo de procesamiento de audio"""
    audio_processing_duration_seconds.labels(operation=operation).observe(duration)

def record_failed_upload(reason='unknown'):
    """Registrar fallo en subida"""
    failed_uploads_total.labels(reason=reason).inc()

def record_supabase_request(operation='upload', success=True):
    """Registrar request a Supabase"""
    status = 'success' if success else 'error'
    supabase_api_requests_total.labels(operation=operation, status=status).inc()

def update_storage_used(bytes_used):
    """Actualizar espacio de almacenamiento usado"""
    music_storage_bytes_used.set(bytes_used)

def update_total_files(count):
    """Actualizar total de archivos de música"""
    music_files_total.set(count)

def record_database_query_time(duration, operation='select'):
    """Registrar tiempo de consulta a BD"""
    database_queries_duration_seconds.labels(operation=operation).observe(duration)

# =============================================================================
# INSTANCIA SINGLETON
# =============================================================================

metrics_middleware = MetricsMiddleware()

# Exportar todo lo necesario
__all__ = [
    'MetricsMiddleware',
    'metrics_middleware',
    'record_music_upload',
    'record_music_download',
    'record_audio_processing_time',
    'record_failed_upload',
    'record_supabase_request',
    'update_storage_used',
    'update_total_files',
    'record_database_query_time'
]