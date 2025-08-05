import os
import jwt
from flask import request, jsonify, g
from functools import wraps

SUPABASE_JWT_SECRET = os.environ.get('SUPABASE_JWT_SECRET')

def verify_jwt(token):
    try:
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated"  # O el valor real de tu proyecto Supabase
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError as e:
        print("Invalid token:", e)  
        return None

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', None)
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization header missing or invalid'}), 401
        token = auth_header.split(' ')[1]
        payload = verify_jwt(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        g.user = payload  # Puedes guardar el payload en g si lo necesitas
        return f(*args, **kwargs)
    return decorated