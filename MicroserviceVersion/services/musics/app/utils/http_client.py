"""
HTTP client utility for inter-service communication
"""
import requests
import logging
from flask import current_app
from functools import wraps

logger = logging.getLogger(__name__)

class ServiceClient:
    """Base class for service-to-service communication"""
    
    def __init__(self, base_url, timeout=5):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
    
    def get(self, endpoint, params=None, headers=None):
        """Make GET request to another service"""
        return self._make_request('GET', endpoint, params=params, headers=headers)
    
    def post(self, endpoint, data=None, json=None, headers=None):
        """Make POST request to another service"""
        return self._make_request('POST', endpoint, data=data, json=json, headers=headers)
    
    def put(self, endpoint, data=None, json=None, headers=None):
        """Make PUT request to another service"""
        return self._make_request('PUT', endpoint, data=data, json=json, headers=headers)
    
    def delete(self, endpoint, headers=None):
        """Make DELETE request to another service"""
        return self._make_request('DELETE', endpoint, headers=headers)
    
    def _make_request(self, method, endpoint, **kwargs):
        """Make HTTP request with error handling"""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            
            logger.info(f"{method} {url} - Status: {response.status_code}")
            
            if response.status_code >= 400:
                logger.error(f"HTTP {response.status_code} - {response.text}")
            
            return response
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout error for {method} {url}")
            raise ServiceTimeoutError(f"Service timeout: {url}")
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error for {method} {url}")
            raise ServiceConnectionError(f"Service connection error: {url}")
        except Exception as e:
            logger.error(f"Unexpected error for {method} {url}: {str(e)}")
            raise ServiceError(f"Service error: {str(e)}")

class ServiceError(Exception):
    """Base exception for service communication errors"""
    pass

class ServiceTimeoutError(ServiceError):
    """Exception for service timeout errors"""
    pass

class ServiceConnectionError(ServiceError):
    """Exception for service connection errors"""
    pass

def with_service_client(service_name):
    """Decorator to inject service client into function"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            service_urls = {
                'user_auth': current_app.config.get('USER_AUTH_SERVICE_URL'),
                'chat': current_app.config.get('CHAT_SERVICE_URL')
            }
            
            if service_name not in service_urls:
                raise ValueError(f"Unknown service: {service_name}")
            
            client = ServiceClient(service_urls[service_name])
            return func(client, *args, **kwargs)
        return wrapper
    return decorator
