from flask import Blueprint, request, jsonify
from app.models.user import User
from app.services.user_service import UserService
from app.utils.responses import ApiResponse
from app.utils.validators import Validators

users_bp = Blueprint('users', __name__)

# Simulamos una base de datos en memoria
users_db = []
user_id_counter = 1

@users_bp.route('/', methods=['GET'])
def get_users():
    """Get all users"""
    return ApiResponse.success([user.to_dict() for user in users_db])

@users_bp.route('/', methods=['POST'])
def create_user():
    """Create a new user"""
    global user_id_counter
    data = request.get_json()
    
    # Validaciones usando el servicio
    errors = UserService.validate_user_data(data)
    if errors:
        return ApiResponse.error('; '.join(errors), 400)
    
    if not Validators.validate_email(data['email']):
        return ApiResponse.error('Invalid email format', 400)
    
    # Verificar si el email ya existe
    if any(user.email == data['email'] for user in users_db):
        return ApiResponse.error('Email already exists', 400)
    
    # Crear usuario
    user = User(
        id=user_id_counter,
        username=data['username'],
        email=data['email']
    )
    
    users_db.append(user)
    user_id_counter += 1
    
    return ApiResponse.success(user.to_dict(), 'User created successfully')

@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user by ID"""
    user = next((u for u in users_db if u.id == user_id), None)
    if not user:
        return ApiResponse.error('User not found', 404)
    
    return ApiResponse.success(user.to_dict())

@users_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update a user"""
    user = next((u for u in users_db if u.id == user_id), None)
    if not user:
        return ApiResponse.error('User not found', 404)
    
    data = request.get_json()
    
    if 'username' in data:
        if len(data['username']) < 3:
            return ApiResponse.error('Username must be at least 3 characters', 400)
        user.username = data['username']
        
    if 'email' in data:
        if not Validators.validate_email(data['email']):
            return ApiResponse.error('Invalid email format', 400)
        # Verificar que el nuevo email no esté en uso por otro usuario
        if any(u.email == data['email'] and u.id != user_id for u in users_db):
            return ApiResponse.error('Email already exists', 400)
        user.email = data['email']
    
    return ApiResponse.success(user.to_dict(), 'User updated successfully')

@users_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user"""
    global users_db
    user = next((u for u in users_db if u.id == user_id), None)
    if not user:
        return ApiResponse.error('User not found', 404)
    
    users_db = [u for u in users_db if u.id != user_id]
    return ApiResponse.success(None, 'User deleted successfully')
