from flask import Blueprint, request, jsonify, g
from app.schemas.auth_schema import LoginRequest, TokenResponse, UserResponse, UserCreate
from app.services.auth_service import AuthService
from app.exceptions.user_exceptions import (
    UserAlreadyExistsException,
    InvalidCredentialsException,
    AuthenticationException
)
import functools  # <-- Agregado
import logging  # <-- Agregado

# ✅ Solo logging básico
from microservice_logging import get_logger

# Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Instancia del servicio
auth_service = AuthService()

# ✅ Logger básico - solo para errores importantes
logger = get_logger("auth_controller")

def handle_service_response(func):
    """Decorador simplificado para manejo de respuestas"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        request_id = getattr(g, 'request_id', 'unknown')
        try:
            result = func(*args, **kwargs)
            return result

        except UserAlreadyExistsException as e:
            logger.warning(f"User exists in {func.__name__}", extra={
                'custom_request_id': request_id
            })
            return jsonify({
                "error": "User already exists",
                "message": str(e),
                "request_id": request_id
            }), 409

        except InvalidCredentialsException as e:
            logger.warning(f"Invalid credentials in {func.__name__}", extra={
                'custom_request_id': request_id
            })
            return jsonify({
                "error": "Invalid credentials",
                "message": str(e),
                "request_id": request_id
            }), 401

        except AuthenticationException as e:
            logger.warning(f"Auth error in {func.__name__}", extra={
                'custom_request_id': request_id
            })
            return jsonify({
                "error": "Authentication error",
                "message": str(e),
                "request_id": request_id
            }), 400

        except ValueError as e:
            logger.error(f"Validation error in {func.__name__}: {str(e)}", extra={
                'custom_request_id': request_id
            })
            return jsonify({
                "error": "Invalid input data",
                "message": str(e),
                "request_id": request_id
            }), 400

        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}", extra={
                'custom_request_id': request_id
            })
            return jsonify({
                "error": "Internal server error",
                "message": str(e),
                "request_id": request_id
            }), 500

    return wrapper

@auth_bp.route('/signup', methods=['POST'])
@handle_service_response
def signup():
    """Endpoint for user signup"""
    request_id = getattr(g, 'request_id', 'unknown')
    
    data = request.get_json()
    if not data:
        return jsonify({
            "error": "No JSON data provided",
            "request_id": request_id
        }), 400
    
    try:
        new_user = UserCreate(**data)
    except Exception as e:
        raise ValueError(f"Invalid user data: {str(e)}")
    
    # Llamar al servicio
    user_response = auth_service.signup(new_user.email, new_user.password)
    
    # ✅ Solo log exitoso si es INFO level
    if logger.isEnabledFor(logging.INFO):
        logger.info("User created", extra={
            'custom_request_id': request_id,
            'custom_email': new_user.email
        })
    
    return jsonify({
        **user_response.dict(),
        "request_id": request_id
    }), 201

@auth_bp.route('/login', methods=['POST'])
@handle_service_response
def login():
    """Endpoint for user login"""
    request_id = getattr(g, 'request_id', 'unknown')
    
    data = request.get_json()
    if not data:
        return jsonify({
            "error": "No JSON data provided",
            "request_id": request_id
        }), 400
    
    try:
        login_request = LoginRequest(**data)
    except Exception as e:
        raise ValueError(f"Invalid login data: {str(e)}")
    
    # Llamar al servicio
    token_response = auth_service.login(login_request)
    
    # ✅ Solo log exitoso si es INFO level
    if logger.isEnabledFor(logging.INFO):
        logger.info("Login successful", extra={
            'custom_request_id': request_id,
            'custom_email': login_request.email
        })
    
    return jsonify({
        **token_response.dict(),
        "request_id": request_id
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@handle_service_response
def logout():
    """Endpoint for user logout"""
    request_id = getattr(g, 'request_id', 'unknown')
    
    auth_header = request.headers.get('Authorization')
    token = None
    
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
    
    success = auth_service.logout(token)
    
    if success:
        return jsonify({
            "message": "Logout successful",
            "request_id": request_id
        }), 200
    else:
        return jsonify({
            "error": "Logout failed",
            "request_id": request_id
        }), 400

# ✅ Endpoints simplificados - resto igual pero sin logging excesivo
@auth_bp.route('/reset-password', methods=['POST'])
@handle_service_response
def reset_password():
    """Endpoint for password reset"""
    request_id = getattr(g, 'request_id', 'unknown')
    
    data = request.get_json()
    if not data:
        return jsonify({
            "error": "No JSON data provided",
            "request_id": request_id
        }), 400
    
    email = data.get('email')
    new_password = data.get('new_password')
    
    if not email or not new_password:
        return jsonify({
            "error": "Email and new_password are required",
            "request_id": request_id
        }), 400
    
    if not auth_service.verify_email_exists(email):
        return jsonify({
            "error": "Email not found",
            "request_id": request_id
        }), 404
    
    success = auth_service.reset_password(email, new_password)
    
    if success:
        return jsonify({
            "message": "Password reset successful",
            "request_id": request_id
        }), 200
    else:
        return jsonify({
            "error": "Password reset failed",
            "request_id": request_id
        }), 400

@auth_bp.route('/verify-email', methods=['POST'])
@handle_service_response
def verify_email():
    """Endpoint to verify if email exists"""
    request_id = getattr(g, 'request_id', 'unknown')
    
    data = request.get_json()
    if not data:
        return jsonify({
            "error": "No JSON data provided",
            "request_id": request_id
        }), 400
    
    email = data.get('email')
    if not email:
        return jsonify({
            "error": "Email is required",
            "request_id": request_id
        }), 400
    
    exists = auth_service.verify_email_exists(email)
    
    return jsonify({
        "email_exists": exists
    }), 200