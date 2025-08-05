import logging
import sys
import os
from datetime import datetime

class SimpleFormatter(logging.Formatter):
    """Formatter simple para desarrollo - menos recursos"""
    
    def format(self, record):
        # Solo campos esenciales
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        service = os.getenv('SERVICE_NAME', 'unknown')
        
        # Formato simple: timestamp - service - level - message
        base_msg = f"{timestamp} - {service} - {record.levelname} - {record.getMessage()}"
        
        # Agregar request_id si existe (campo más importante)
        request_id = getattr(record, 'custom_request_id', None)
        if request_id:
            base_msg += f" [ID: {request_id}]"
        
        # Solo agregar excepción si es ERROR o CRITICAL
        if record.exc_info and record.levelno >= logging.ERROR:
            base_msg += f" - ERROR: {record.exc_info[1]}"
        
        return base_msg

def get_logger(name: str = None) -> logging.Logger:
    """Logger básico optimizado para práctica"""
    logger_name = name or os.getenv('SERVICE_NAME', 'microservice')
    log_level = os.getenv('LOG_LEVEL', 'WARNING').upper()  # WARNING por defecto para menos logs
    
    logger = logging.getLogger(logger_name)
    
    # Evitar duplicar handlers
    if logger.handlers:
        return logger
        
    logger.setLevel(getattr(logging, log_level))
    
    # Solo formato simple
    formatter = SimpleFormatter()
    
    # Handler único para stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    logger.propagate = False
    
    return logger

def configure_root_logger():
    """Configuración mínima del logger raíz"""
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # WARNING por defecto para reducir volumen de logs
    log_level = os.getenv('LOG_LEVEL', 'WARNING').upper()
    root_logger.setLevel(getattr(logging, log_level))