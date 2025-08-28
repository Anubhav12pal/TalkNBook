from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """Model for user creation request."""
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """Model for user login request."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Model for user response (without password)."""
    id: str
    username: str
    email: str
    created_at: datetime


class Token(BaseModel):
    """Model for token response."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Model for token data."""
    email: Optional[str] = None