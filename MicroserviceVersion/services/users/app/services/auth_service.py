"""
Authentication service with proper error handling and best practices
"""
from typing import Optional, Dict, Any
from app.core.supabase import get_supabase, get_supabase_admin
from app.schemas.auth_schema import LoginRequest, TokenResponse, UserResponse
from app.exceptions.user_exceptions import (
    UserAlreadyExistsException,
    InvalidCredentialsException,
    AuthenticationException,
    UserNotFoundException
)
import logging

logger = logging.getLogger("auth_service")


class AuthService:
    """Service class for authentication-related operations"""

    def __init__(self):
        self.supabase = get_supabase()
        self.supabase_admin = get_supabase_admin()

    def find_user_by_email(self, email: str) -> Optional[dict]:
        """
        Busca un usuario por email en todas las páginas de Supabase.
        Devuelve el dict del usuario si lo encuentra, None si no existe.
        """
        try:
            page = 1
            per_page = 100

            while True:
                logger.debug(f"[DEBUG] Buscando usuarios en página {page}")

                # Obtener usuarios de la página actual
                users_response = self.supabase_admin.auth.admin.list_users(
                    page=page, per_page=per_page)

                # Manejo robusto de la respuesta
                users = []
                if hasattr(users_response, 'data'):
                    users = users_response.data or []
                elif isinstance(users_response, dict):
                    users = users_response.get('data', [])
                elif isinstance(users_response, list):
                    users = users_response

                logger.debug(
                    f"[DEBUG] Encontrados {len(users)} usuarios en página {page}")

                if not users:
                    logger.debug(
                        f"[DEBUG] No hay más usuarios en página {page}")
                    break

                # Buscar el usuario por email
                for user in users:
                    user_email = ""
                    if hasattr(user, 'email'):
                        user_email = user.email
                    elif isinstance(user, dict):
                        user_email = user.get("email", "")

                    target_email = email.lower().strip()
                    user_email_clean = user_email.lower().strip()

                    logger.debug(
                        f"[DEBUG] Comparando '{user_email_clean}' con '{target_email}'")

                    if user_email_clean == target_email:
                        user_id = user.id if hasattr(
                            user, 'id') else user.get('id', 'N/A')
                        logger.debug(f"[DEBUG] Usuario encontrado: {user_id}")
                        return user if isinstance(user, dict) else {
                            'id': user.id,
                            'email': user.email,
                            'created_at': getattr(user, 'created_at', None)
                        }

                # Si hay menos usuarios que el límite por página, hemos llegado al final
                if len(users) < per_page:
                    logger.debug(
                        f"[DEBUG] Última página alcanzada (menos de {per_page} usuarios)")
                    break

                page += 1

            logger.debug(
                f"[DEBUG] Usuario con email '{email}' no encontrado después de revisar todas las páginas")
            return None

        except Exception as e:
            logger.error(f"[ERROR] Error en find_user_by_email: {repr(e)}")
            return None

    def verify_email_exists(self, email: str) -> bool:
        """
        Verifica si el email existe realmente en Supabase usando paginación robusta.
        """
        try:
            logger.debug(f"[DEBUG] Verificando existencia de email: {email}")
            user = self.find_user_by_email(email)

            if user:
                user_id = user.get('id', 'N/A') if isinstance(user,
                                                              dict) else getattr(user, 'id', 'N/A')
                logger.debug(
                    f"[DEBUG] Usuario encontrado en verify_email_exists: {user_id}")
                return True

            logger.debug(
                f"[DEBUG] Usuario NO encontrado en verify_email_exists para email: {email}")
            return False

        except Exception as e:
            logger.error(f"[ERROR] Error en verify_email_exists: {repr(e)}")
            return False

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
                raise UserAlreadyExistsException(
                    f"User with email {email} already exists")

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

    def reset_password(self, email: str, new_password: str) -> bool:
        """
        Reset user password directly usando búsqueda robusta por email.
        """
        try:
            logger.debug(
                f"[DEBUG] Iniciando reset_password para email: {email}")
            user = self.find_user_by_email(email)

            if not user:
                logger.debug(
                    f"[DEBUG] Usuario NO encontrado en reset_password para email: {email}")
                raise UserNotFoundException(
                    f"User with email '{email}' not found")

            user_id = user.get("id") if isinstance(
                user, dict) else getattr(user, 'id', None)
            logger.debug(
                f"[DEBUG] Usuario encontrado en reset_password: {user_id}")

            response = self.supabase_admin.auth.admin.update_user_by_id(
                user_id,
                {"password": new_password}
            )

            # Verificar la respuesta
            user_obj = None
            if hasattr(response, "user"):
                user_obj = response.user
            elif isinstance(response, dict) and "user" in response:
                user_obj = response["user"]
            elif isinstance(response, dict) and "data" in response:
                user_obj = response["data"]

            if not user_obj:
                logger.debug(
                    f"[DEBUG] Respuesta inesperada en reset_password: {response}")
                raise AuthenticationException(
                    f"Password reset failed: respuesta inesperada")

            logger.debug(
                f"[DEBUG] Password reset exitoso para usuario: {user_id}")
            return True

        except UserNotFoundException:
            raise
        except AuthenticationException:
            raise
        except Exception as e:
            logger.error(f"[ERROR] Error en reset_password: {repr(e)}")
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

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return user data"""
        try:
            # Set the session with the token
            self.supabase.auth.set_session(token, "")

            # Get the current user
            user = self.supabase.auth.get_user()

            if not user or not user.user:
                return None

            return {
                "user_id": user.user.id,
                "email": user.user.email
            }

        except Exception as e:
            logger.debug(f"[DEBUG] Error verifying token: {repr(e)}")
            return None

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
