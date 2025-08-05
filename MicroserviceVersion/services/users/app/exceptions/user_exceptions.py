"""
    Custom exceptions for user-related errors in the authentication service.
"""

class BaseUserException(Exception):
    """Base class for user-related exceptions."""

    def __init__(self, message: str = "An error occurred", error_code: int = 400):
        self.message = message
        self.error_code = error_code
        super().__init__(message)

    def to_dict(self):
        """Convert the exception to a dictionary."""
        return {
            "error": self.message,
            "code": self.error_code
        }

class UserAlreadyExistsException(BaseUserException):
    """Exception raised when a user already exists."""

    def __init__(self, message: str = "User already exists", error_code: int = 409):
        super().__init__(message, error_code)


class UserNotFoundException(BaseUserException):
    """Exception raised when a user is not found."""

    def __init__(self, message: str = "User not found", error_code: int = 404):
        super().__init__(message, error_code)

class InvalidCredentialsException(BaseUserException):
    """Exception raised for invalid user credentials."""

    def __init__(self, message: str = "Invalid credentials", error_code: int = 401):
        super().__init__(message, error_code)

class AuthenticationException(BaseUserException):
    """Exception raised for authentication errors."""

    def __init__(self, message: str = "Authentication failed", error_code: int = 401):
        super().__init__(message, error_code)
