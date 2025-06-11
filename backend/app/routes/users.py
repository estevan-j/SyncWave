from flask import Blueprint, request, jsonify
from app.models.database import db, User
from app.services.user_service import UserService
from app.utils.responses import ApiResponse
from app.utils.validators import Validators
from werkzeug.security import generate_password_hash, check_password_hash

users_bp = Blueprint('users', __name__)

@users_bp.route('/', methods=['GET'])
def get_users():
    """Get all users"""
    users = User.query.all()
    return ApiResponse.success([user.to_dict() for user in users])

@users_bp.route('/', methods=['POST'])
def create_user():
    """Create a new user"""
    data = request.get_json()
    
    # Validaciones básicas
    if not data or 'email' not in data or 'password' not in data:
        return ApiResponse.error('Email and password are required', 400)
    
    if not Validators.validate_email(data['email']):
        return ApiResponse.error('Invalid email format', 400)
    
    # Verificar si el email ya existe
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return ApiResponse.error('Email already exists', 400)
    
    # Validar longitud de password
    if len(data['password']) < 6:
        return ApiResponse.error('Password must be at least 6 characters long', 400)
    
    try:
        # Crear usuario con password hasheado
        user = User(
            email=data['email'],
            password=generate_password_hash(data['password'])
        )
        
        db.session.add(user)
        db.session.commit()
        
        return ApiResponse.success(user.to_dict(), 'User created successfully')
        
    except Exception as e:
        db.session.rollback()
        return ApiResponse.error(f"Error creating user: {str(e)}", 500)

@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user by ID"""
    user = User.query.get_or_404(user_id)
    return ApiResponse.success(user.to_dict())

@users_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update a user"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    try:
        if 'email' in data:
            if not Validators.validate_email(data['email']):
                return ApiResponse.error('Invalid email format', 400)
            # Verificar que el nuevo email no esté en uso por otro usuario
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user_id:
                return ApiResponse.error('Email already exists', 400)
            user.email = data['email']
        
        if 'password' in data:
            if len(data['password']) < 6:
                return ApiResponse.error('Password must be at least 6 characters long', 400)
            user.password = generate_password_hash(data['password'])
        
        db.session.commit()
        return ApiResponse.success(user.to_dict(), 'User updated successfully')
        
    except Exception as e:
        db.session.rollback()
        return ApiResponse.error(f"Error updating user: {str(e)}", 500)

@users_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user"""
    user = User.query.get_or_404(user_id)
    
    try:
        db.session.delete(user)
        db.session.commit()
        return ApiResponse.success({}, 'User deleted successfully')
        
    except Exception as e:
        db.session.rollback()
        return ApiResponse.error(f"Error deleting user: {str(e)}", 500)

@users_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return ApiResponse.error('Email and password are required', 400)
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not check_password_hash(user.password, data['password']):
        return ApiResponse.error('Invalid email or password', 401)
    
    return ApiResponse.success({
        'user': user.to_dict(),
        'message': 'Login successful'
    })

@users_bp.route('/check-email', methods=['POST'])
def check_email():
    """Check if email exists"""
    data = request.get_json()
    
    if not data or 'email' not in data:
        return ApiResponse.error('Email is required', 400)
    
    existing_user = User.query.filter_by(email=data['email']).first()
    
    return ApiResponse.success({
        'email': data['email'],
        'exists': existing_user is not None
    })

@users_bp.route('/search', methods=['GET'])
def search_users():
    """Search users by email"""
    query = request.args.get('q', '').lower()
    
    if len(query) < 2:
        return ApiResponse.error('Search query must be at least 2 characters', 400)
    
    users = User.query.filter(User.email.contains(query)).all()
    
    return ApiResponse.success([user.to_dict() for user in users])

@users_bp.route('/verify-email', methods=['POST'])
def verify_email():
    """Verify if email exists for password recovery"""
    data = request.get_json()
    
    if not data or 'email' not in data:
        return ApiResponse.error('Email is required', 400)
    
    if not Validators.validate_email(data['email']):
        return ApiResponse.error('Invalid email format', 400)
    
    # Check if user exists
    user = User.query.filter_by(email=data['email']).first()
    
    if not user:
        return ApiResponse.error('No account found with this email address', 404)
    
    return ApiResponse.success({
        'email': data['email'],
        'exists': True,
        'message': 'Email verified successfully'
    })

@users_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset user password"""
    data = request.get_json()
    
    if not data or 'email' not in data or 'newPassword' not in data:
        return ApiResponse.error('Email and new password are required', 400)
    
    if not Validators.validate_email(data['email']):
        return ApiResponse.error('Invalid email format', 400)
    
    if len(data['newPassword']) < 6:
        return ApiResponse.error('Password must be at least 6 characters long', 400)
    
    try:
        # Find user by email
        user = User.query.filter_by(email=data['email']).first()
        
        if not user:
            return ApiResponse.error('No account found with this email address', 404)
        
        # Update password
        user.password = generate_password_hash(data['newPassword'])
        db.session.commit()
        
        return ApiResponse.success({
            'message': 'Password updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return ApiResponse.error(f"Error updating password: {str(e)}", 500)
