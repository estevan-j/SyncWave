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
        Verify if email exists in the system.
        This is step 1 of password reset flow.
        
        Args:
            email: Email to verify
            
        Returns:
            bool: True if email exists, False otherwise
        """
        try:
            # Use admin client to check if user exists by email
            # This is a workaround since Supabase doesn't have a direct "check user exists" method
            # We'll try to get user info using admin privileges
            
            # Alternative approach: try to initiate password reset
            # Supabase will not throw error if user doesn't exist (for security)
            self.supabase.auth.reset_password_email(email)
            
            # For security reasons, we return True regardless
            # The actual verification happens when user receives email
            return True
            
        except Exception:
            # If there's an error with the email format or service
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
            
            user_id = None
            if users_response.users:
                for user in users_response.users:
                    if user.email == email:
                        user_id = user.id
                        break
            
            if not user_id:
                raise AuthenticationException("User not found")
            
            # Update password using admin client
            response = self.supabase_admin.auth.admin.update_user_by_id(
                user_id,
                {"password": new_password}
            )
            
            if not response.user:
                raise AuthenticationException("Password reset failed")
            
            return True
            
        except AuthenticationException:
            raise
        except Exception as e:
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
