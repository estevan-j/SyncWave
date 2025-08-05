"""
Microservice Logging Library
Shared logging utilities for Flask microservices
"""
from .logger import get_logger, configure_root_logger
from .middleware import setup_request_logging

__version__ = "1.0.0"
__all__ = [
    "get_logger",
    "configure_root_logger", 
    "JSONFormatter",
    "setup_request_logging"
]