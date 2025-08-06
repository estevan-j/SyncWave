"""
Authentication service with proper error handling and best practices
"""
from typing import Optional, Dict, Any
from app.core.supabase import get_supabase, get_supabase_admin
from app.schemas.auth_schema import LoginRequest, TokenResponse, UserResponse
from app.exceptions.user_exceptions import (
    UserAlreadyExistsException,
    InvalidCredentialsException,
    AuthenticationException
)


class AuthService:
    from microservice_logging import get_logger
    logger = get_logger("auth_service")
    def find_user_by_email(self, email: str) -> Optional[dict]:
        """
        Busca un usuario por email en todas las páginas de Supabase.
        Devuelve el dict del usuario si lo encuentra, None si no existe.
        """
        try:
            page = 1
            per_page = 100
            while True:
                users_response = self.supabase_admin.auth.admin.list_users(page=page, per_page=per_page)
                users = users_response.data if hasattr(users_response, 'data') else users_response.get('data', [])
                if not users:
                    break
                for user in users:
                    if user.get("email", "").lower() == email.lower():
                        return user
                if len(users) < per_page:
                    break
                page += 1
            return None
        except Exception as e:
            self.logger.debug(f"[DEBUG] Error en find_user_by_email: {repr(e)}")
            return None
    """Service class for authentication-related operations"""

    def __init__(self):
        self.supabase = get_supabase()
        self.supabase_admin = get_supabase_admin()

    def signup(self, email: str, password: str) -> UserResponse:
        """Create a new user account"""
        try:
            response = self.supabase_admin.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True
            })
            
            if not response.user:
                raise AuthenticationException("User creation failed")
            
            return UserResponse(
                id=response.user.id,
                name=response.user.email,
                email=response.user.email
            )
            
        except Exception as e:
            error_message = str(e).lower()
            
            if any(keyword in error_message for keyword in [
                "already registered", "already exists", "duplicate"
            ]):
                raise UserAlreadyExistsException(f"User with email {email} already exists")
            
            raise AuthenticationException(f"Signup failed: {str(e)}")

    def login(self, login_request: LoginRequest) -> TokenResponse:
        """Authenticate user and return token"""
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": login_request.email,
                "password": login_request.password
            })
            
            if not response.user or not response.session:
                raise InvalidCredentialsException("Invalid email or password")
            
            return TokenResponse(
                access_token=response.session.access_token,
                token_type="bearer"
            )
            
        except Exception as e:
            error_message = str(e).lower()
            
            if any(keyword in error_message for keyword in [
                "invalid login", "invalid credentials", "wrong password"
            ]):
                raise InvalidCredentialsException("Invalid email or password")
            
            raise AuthenticationException(f"Login failed: {str(e)}")


    def verify_email_exists(self, email: str) -> bool:
        """
        Verifica si el email existe realmente en Supabase usando paginación robusta.
        """
        user = self.find_user_by_email(email)
        if user:
            self.logger.debug(f"[DEBUG] Usuario encontrado en verify_email_exists: {user}")
            return True
        self.logger.debug(f"[DEBUG] Usuario NO encontrado en verify_email_exists para email: {email}")
        return False

def reset_password(self, email: str, new_password: str) -> bool:
    """
    Reset user password directly.
    This is step 2 of password reset flow (after email verification).

    Args:
        email: User's email
        new_password: New password to set

    Returns:
        bool: True if password reset successful

    Raises:
        AuthenticationException: If reset fails
    """
    try:
        # Get user by email using admin client
        users_response = self.supabase_admin.auth.admin.list_users()
        users = users_response.data if hasattr(users_response, 'data') else users_response.get('data', [])
        user_id = None
        for user in users:
            if user.get("email", "").lower() == email.lower():
                user_id = user.get("id")
                break

        if not user_id:
            raise AuthenticationException("User not found")

        # Update password using admin client
        response = self.supabase_admin.auth.admin.update_user_by_id(
            user_id,
            {"password": new_password}
        )

        user_obj = None
        if hasattr(response, "user"):
            user_obj = response.user
        elif isinstance(response, dict) and "user" in response:
            user_obj = response["user"]
        elif isinstance(response, dict) and "data" in response:
            user_obj = response["data"]

        if not user_obj:
            raise AuthenticationException("Password reset failed")

        return True

    except AuthenticationException:
        raise
    except Exception as e:
        raise AuthenticationException(f"Password reset failed: {str(e)}")
        """
        Reset user password directly usando búsqueda robusta por email.
        Lanza UserNotFoundException si el usuario no existe.
        """
        try:
            user = self.find_user_by_email(email)
            if not user:
                self.logger.debug(f"[DEBUG] Usuario NO encontrado en reset_password para email: {email}")
                from app.exceptions.user_exceptions import UserNotFoundException
                raise UserNotFoundException(f"User with email '{email}' not found")
            user_id = user.get("id")
            self.logger.debug(f"[DEBUG] Usuario encontrado en reset_password: {user}")
            response = self.supabase_admin.auth.admin.update_user_by_id(
                user_id,
                {"password": new_password}
            )
            user_obj = None
            if hasattr(response, "user"):
                user_obj = response.user
            elif isinstance(response, dict) and "user" in response:
                user_obj = response["user"]
            elif isinstance(response, dict) and "data" in response:
                user_obj = response["data"]
            if not user_obj:
                self.logger.debug(f"[DEBUG] Respuesta inesperada en reset_password: {response}")
                raise AuthenticationException(f"Password reset failed: respuesta inesperada {response}")
            return True
        except UserNotFoundException:
            raise
        except AuthenticationException:
            raise
        except Exception as e:
            self.logger.debug(f"[DEBUG] Error en reset_password: {repr(e)}")
            raise AuthenticationException(f"Password reset failed: {str(e)}")

    def logout(self, token: Optional[str] = None) -> bool:
        """Sign out user"""
        try:
            if token:
                self.supabase.auth.set_session(token, "")
            
            self.supabase.auth.sign_out()
            return True
            
        except Exception:
            return False

    def get_current_user(self, token: str) -> Optional[UserResponse]:
        """Get current user from token"""
        try:
            user_data = self.verify_token(token)
            
            if not user_data:
                return None
            
            return UserResponse(
                id=user_data["user_id"],
                name=user_data["email"],
                email=user_data["email"]
            )
            
        except Exception:
            return None
