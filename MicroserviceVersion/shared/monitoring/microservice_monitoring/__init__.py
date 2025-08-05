"""
Microservice Monitoring - Configuración básica
"""

from .metrics import setup_basic_metrics, request_count, error_count
from .health import setup_basic_health

__version__ = "1.0.0"
__all__ = [
    "setup_basic_metrics",
    "setup_basic_health", 
    "request_count",
    "error_count"
]