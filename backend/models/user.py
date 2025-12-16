"""User model for authentication."""
from pydantic import BaseModel, EmailStr, Field, BeforeValidator
from typing import Annotated, Optional
from datetime import datetime, timezone
from bson import ObjectId


# Custom type for MongoDB ObjectId that converts to string
PyObjectId = Annotated[str, BeforeValidator(lambda v: str(v) if isinstance(v, ObjectId) else v)]


class User(BaseModel):
    """User model for MongoDB storage."""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    email: EmailStr
    name: str
    password_hash: str
    reset_token: Optional[str] = None
    reset_token_expires: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
        "json_schema_extra": {
            "example": {
                "email": "sarah@example.com",
                "name": "Sarah Chen",
                "password_hash": "$argon2id$v=19$m=65536...",
                "created_at": "2025-12-15T10:00:00Z",
                "updated_at": "2025-12-15T10:00:00Z"
            }
        }
    }


class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    name: str
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response (without password)."""
    id: str
    email: str
    name: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "email": "sarah@example.com",
                "name": "Sarah Chen"
            }
        }
    }


class AuthResponse(BaseModel):
    """Schema for authentication response."""
    user: UserResponse
    token: str


class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""
    email: EmailStr


class PasswordReset(BaseModel):
    """Schema for password reset."""
    token: str
    new_password: str = Field(min_length=8)


class PasswordResetDirect(BaseModel):
    """Schema for direct password reset without token."""
    email: EmailStr
    new_password: str = Field(min_length=8)


class MessageResponse(BaseModel):
    """Schema for simple message response."""
    message: str
    reset_token: Optional[str] = None  # Only populated in development mode