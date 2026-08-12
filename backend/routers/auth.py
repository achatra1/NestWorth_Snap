"""Authentication routes for user signup, login, logout, and profile."""
import logging
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import jwt
import secrets
from datetime import datetime, timezone, timedelta
from bson import ObjectId

from backend.models.user import (
    User, UserCreate, UserLogin, UserResponse, AuthResponse,
    PasswordResetRequest, PasswordReset, MessageResponse
)
from backend.database import get_database
from backend.config import settings
from backend.integrations.email_client import send_password_reset_email

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
security = HTTPBearer()
ph = PasswordHasher()


def create_jwt_token(user_id: str) -> str:
    """Create JWT token for user."""
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(seconds=settings.JWT_EXPIRES_IN),
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def verify_jwt_token(token: str) -> str:
    """Verify JWT token and return user_id."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Dependency to get current authenticated user."""
    user_id = verify_jwt_token(credentials.credentials)
    db = get_database()
    
    user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return User(**user_doc)


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate):
    """Register a new user account."""
    db = get_database()
    
    # Check if email already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        logger.warning(f"Signup rejected, email already registered: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    password_hash = ph.hash(user_data.password)
    
    # Create user document
    user = User(
        email=user_data.email,
        name=user_data.name,
        password_hash=password_hash,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    # Insert into database
    result = await db.users.insert_one(user.model_dump(by_alias=True, exclude={"id"}))
    user.id = str(result.inserted_id)
    
    # Generate JWT token
    token = create_jwt_token(user.id)

    logger.info(f"New user signed up: {user.email} (id={user.id})")

    # Return user and token
    return AuthResponse(
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name
        ),
        token=token
    )


@router.post("/login", response_model=AuthResponse)
async def login(credentials: UserLogin):
    """Authenticate existing user and return JWT token."""
    db = get_database()
    
    # Find user by email
    user_doc = await db.users.find_one({"email": credentials.email})
    if not user_doc:
        logger.warning(f"Login failed, no account for email: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    user = User(**user_doc)

    # Verify password
    try:
        ph.verify(user.password_hash, credentials.password)
    except VerifyMismatchError:
        logger.warning(f"Login failed, bad password for email: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Generate JWT token
    token = create_jwt_token(user.id)

    logger.info(f"User logged in: {user.email} (id={user.id})")

    # Return user and token
    return AuthResponse(
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name
        ),
        token=token
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout user (client-side token removal)."""
    logger.info(f"User logged out: {current_user.email} (id={current_user.id})")
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name
    )


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(request: PasswordResetRequest):
    """Request password reset token."""
    db = get_database()
    
    # Find user by email
    user_doc = await db.users.find_one({"email": request.email})
    
    # Always return success message to prevent email enumeration
    if not user_doc:
        logger.info(f"Password reset requested for unknown email: {request.email}")
        return MessageResponse(
            message="If an account exists with this email, a password reset link will be sent."
        )
    
    # Generate secure reset token
    reset_token = secrets.token_urlsafe(32)
    reset_token_expires = datetime.now(timezone.utc) + timedelta(hours=1)

    # Update user with reset token
    await db.users.update_one(
        {"_id": user_doc["_id"]},
        {
            "$set": {
                "reset_token": reset_token,
                "reset_token_expires": reset_token_expires,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )

    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

    if settings.RESEND_API_KEY:
        try:
            await send_password_reset_email(request.email, reset_url)
            logger.info(f"Password reset email sent to {request.email}")
        except Exception:
            logger.exception(f"Failed to send password reset email to {request.email}")

        return MessageResponse(
            message="If an account exists with this email, a password reset link will be sent."
        )

    # No email provider configured: fall back to logging the link.
    # Only return the token directly in development, so a misconfigured
    # production deployment doesn't leak reset tokens over the API.
    logger.info(f"Password reset requested for {request.email}, reset URL: {reset_url}")

    if settings.APP_ENV == "development":
        return MessageResponse(
            message="If an account exists with this email, a password reset link will be sent.",
            reset_token=reset_token
        )

    logger.warning("RESEND_API_KEY is not configured; password reset email was not sent")
    return MessageResponse(
        message="If an account exists with this email, a password reset link will be sent."
    )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(reset_data: PasswordReset):
    """Reset password using token."""
    db = get_database()
    
    # Find user with valid reset token
    user_doc = await db.users.find_one({
        "reset_token": reset_data.token,
        "reset_token_expires": {"$gt": datetime.now(timezone.utc)}
    })
    
    if not user_doc:
        logger.warning("Password reset attempted with invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Hash new password
    password_hash = ph.hash(reset_data.new_password)
    
    # Update password and clear reset token
    await db.users.update_one(
        {"_id": user_doc["_id"]},
        {
            "$set": {
                "password_hash": password_hash,
                "updated_at": datetime.now(timezone.utc)
            },
            "$unset": {
                "reset_token": "",
                "reset_token_expires": ""
            }
        }
    )
    
    logger.info(f"Password reset completed for user id={user_doc['_id']}")

    return MessageResponse(message="Password has been reset successfully")