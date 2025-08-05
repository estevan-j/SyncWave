from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List


class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="The user's email address")
    password: str = Field(..., min_length=8, description="The user's password")

class UserResponse(BaseModel):
    id: int
    name: str
    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None, description="The user's email address")
    password: Optional[str] = Field(None, min_length=8, description="The user's password")
    
class TokenResponse(BaseModel):
    access_token: str = Field(..., description="The access token for the user")
    token_type: str = Field(default="bearer", description="The type of the token")


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="The user's email address")
    password: str 


class EmailVerificationRequest(BaseModel):
    """Schema for email verification (step 1 of password reset)"""
    email: EmailStr = Field(..., description="Email to verify")

class PasswordResetRequest(BaseModel):
    """Schema for password reset (step 2 of password reset)"""
    email: EmailStr = Field(..., description="User's email")
    new_password: str = Field(..., min_length=8, description="New password")