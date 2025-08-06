"""
Custom exceptions for chat-related errors in the users service.
"""

class BaseChatException(Exception):
    """Base class for chat-related exceptions."""

    def __init__(self, message: str = "A chat error occurred", error_code: int = 400):
        self.message = message
        self.error_code = error_code
        super().__init__(message)

    def to_dict(self):
        """Convert the exception to a dictionary."""
        return {
            "error": self.message,
            "code": self.error_code
        }


class MessageValidationException(BaseChatException):
    """Exception raised when message validation fails."""

    def __init__(self, message: str = "Message validation failed", error_code: int = 400):
        super().__init__(message, error_code)


class MessageNotFoundException(BaseChatException):
    """Exception raised when a message is not found."""

    def __init__(self, message: str = "Message not found", error_code: int = 404):
        super().__init__(message, error_code)


class UnauthorizedMessageException(BaseChatException):
    """Exception raised when user is not authorized to perform action on message."""

    def __init__(self, message: str = "Unauthorized to perform this action", error_code: int = 403):
        super().__init__(message, error_code)


class RoomNotFoundException(BaseChatException):
    """Exception raised when a chat room is not found."""

    def __init__(self, message: str = "Chat room not found", error_code: int = 404):
        super().__init__(message, error_code)


class UserNotInRoomException(BaseChatException):
    """Exception raised when user is not in the specified room."""

    def __init__(self, message: str = "User not in room", error_code: int = 400):
        super().__init__(message, error_code)


class ChatServiceException(BaseChatException):
    """Exception raised for general chat service errors."""

    def __init__(self, message: str = "Chat service error", error_code: int = 500):
        super().__init__(message, error_code) 