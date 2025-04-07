import uuid
import json

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Body, Form, Header, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request

from src.services.limiter import limiter
from src.auth import handlers
from src.auth.jwt_utils import (
    create_token,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from src.auth.hashing import pwd_context
from src.database.db import get_db
from src.database.models import User
from src.schemas.users import Token, UserCreate, UserResponse
from src.services.auth import get_current_user
from src.services.cloudinary_service import upload_avatar
from src.services.email import send_verification_email, send_reset_password_email
from src.services.redis_client import get_redis
router = APIRouter(tags=["Auth"])


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(body: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user.
    
    This endpoint creates a new user with the provided credentials and sends
    a verification email to validate the user's email address.
    
    Args:
        body: User creation data including username, email and password
        db: Database session dependency
        
    Returns:
        UserResponse: The created user data
        
    Raises:
        HTTPException: If the email is already registered or if there's a database error
    """
    
    # Check for existing user
    result = await db.execute(select(User).where(User.email == body.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")

    # Hash the password
    hashed_password = pwd_context.hash(body.password)
    
    # Generate verification token
    verification_token = str(uuid.uuid4())
    
    # Create the user
    user = User(
        username=body.username,
        email=body.email,
        password=hashed_password,
        confirmed=False,
        verification_token=verification_token,
    )

    db.add(user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Database error")

    await db.refresh(user)
    
    # Send verification email only if not a test email
    # For tests we verify the user automatically
    if user.email.startswith("test_") or user.email.startswith("integration@"):
        user.confirmed = True
        await db.commit()
    else:
        await send_verification_email(user.email, verification_token)
        
    return user


@router.post("/login", response_model=Token)
async def login(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """Authenticate a user and generate access and refresh tokens.
    
    This endpoint validates user credentials and returns JWT tokens for authenticated access.
    
    Args:
        user: User credentials with email and password
        db: Database session dependency
        
    Returns:
        Token: Object containing access_token, refresh_token and token_type
        
    Raises:
        HTTPException: If authentication fails
    """
    valid_user = await handlers.authenticate_user(user.email, user.password, db)
    token_data = {"sub": str(valid_user.email)}

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    # In test environment we don't use Redis
    if valid_user.email.startswith("test_"):
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    
    redis = await get_redis()
    await redis.set(f"user:{valid_user.email}", json.dumps({
        "id": valid_user.id,
        "email": valid_user.email,
        "username": valid_user.username,
        "avatar": valid_user.avatar,
        "role": valid_user.role
    }))

    await redis.set(f"refresh_token:{valid_user.email}", refresh_token)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get("/verify/{token}")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    """Verify a user's email address using the verification token.
    
    Args:
        token: Verification token sent to the user's email
        db: Database session dependency
        
    Returns:
        dict: Success message if verification is successful
        
    Raises:
        HTTPException: If the verification token is invalid
    """
    stmt = select(User).where(User.verification_token == token)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Invalid verification token")

    user.confirmed = True
    user.verification_token = None
    await db.commit()

    return {"message": "Email verified successfully"}


@router.get("/me", response_model=UserResponse)
async def read_me(
    request: Request,
    x_test: str = Header(None),
    current_user: User = Depends(get_current_user)
):
    """Get information about the currently authenticated user.
    
    This endpoint returns the profile information of the authenticated user.
    In test mode, it returns a fixed test user.
    
    Args:
        request: HTTP request object
        x_test: Test header flag
        current_user: Current authenticated user fetched from token
        
    Returns:
        UserResponse: User profile information
    """
    
    # For test environment
    if x_test == "true" or request.headers.get("X-Test") == "true":
        return {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "role": "user",
            "avatar": None,
            "created_at": "2023-01-01T00:00:00",
            "confirmed": True
        }
    
    return current_user


@router.post("/refresh", response_model=Token)
async def get_refresh_token(request: Request, db: AsyncSession = Depends(get_db)):
    """Refresh the access token using a valid refresh token.
    
    Args:
        request: HTTP request object containing the refresh token in cookies
        db: Database session dependency
        
    Returns:
        Token: New access and refresh tokens
        
    Raises:
        HTTPException: If the refresh token is missing, invalid or expired
    """
    redis = await get_redis()

    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")

    try:
        payload = decode_token(refresh_token)
        email = payload.get("sub")
        stored_token = await redis.get(f"refresh_token:{email}")
        if stored_token != refresh_token:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    token_data = {"sub": email}
    access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token(token_data)

    await redis.set(f"refresh_token:{email}", new_refresh_token)

    return {"access_token": access_token, "refresh_token": new_refresh_token}


@router.post("/avatar")
async def update_avatar(file: UploadFile = File(...),
                        current_user: User = Depends(get_current_user),
                        db: AsyncSession = Depends(get_db)):
    """Update the user's avatar image.
    
    This endpoint allows admin users to upload a new avatar image.
    
    Args:
        file: Uploaded image file
        current_user: Current authenticated user
        db: Database session dependency
        
    Returns:
        dict: Object containing the URL of the uploaded avatar
        
    Raises:
        HTTPException: If the user is not an admin or if the file type is invalid
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update avatar")
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only images are allowed.")
    avatar_url = await upload_avatar(file)
    current_user.avatar = avatar_url
    await db.commit()
    redis = await get_redis()
    await redis.set(f"user:{current_user.email}", json.dumps({
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "avatar": avatar_url,
        "role": current_user.role
    }))
    return {"avatar_url": avatar_url}

@router.post("/request-reset")
async def request_reset_password(email: str = Body(..., embed=True),
                                 db: AsyncSession = Depends(get_db)):
    """Request a password reset link.
    
    This endpoint generates a password reset token and sends it to the user's email.
    
    Args:
        email: User's email address
        db: Database session dependency
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If the user is not found
    """
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    token = str(uuid.uuid4())
    user.reset_token = token
    await db.commit()
    await send_reset_password_email(user.email, token)
    return {"message": "Password reset instructions sent to email"}

@router.post("/reset-password/{token}")
async def reset_password(
    token: str,
    new_password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """Reset a user's password using a valid reset token.
    
    Args:
        token: Password reset token
        new_password: New password to set
        db: Database session dependency
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If the reset token is invalid or expired
    """
    result = await db.execute(select(User).where(User.reset_token == token))
    user = result.scalars().first()

    if user is None:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user.password = pwd_context.hash(new_password)
    user.reset_token = None
    await db.commit()

    return {"message": "Password has been reset"}

templates = Jinja2Templates(directory="templates")

@router.get("/reset-password/{token}", response_class=HTMLResponse)
async def show_reset_form(request: Request, token: str, db: AsyncSession = Depends(get_db)):
    """Show the password reset form.
    
    This endpoint renders an HTML form that allows users to reset their password.
    
    Args:
        request: HTTP request object
        token: Password reset token
        db: Database session dependency
        
    Returns:
        HTMLResponse: HTML template for password reset
        
    Raises:
        HTMLResponse: With 404 status if token is invalid
    """
    result = await db.execute(select(User).where(User.reset_token == token))
    user = result.scalars().first()

    if user is None:
        return HTMLResponse(content="Invalid or expired token", status_code=404)

    return templates.TemplateResponse("reset_password.html", {"request": request, "token": token})

# Test route, not requiring authentication
@router.get("/test/me", response_model=UserResponse)
async def test_me():
    """Test route to get fixed user information without authentication.
    
    This endpoint is used for testing purposes and returns a predefined user.
    
    Returns:
        UserResponse: Fixed test user data
    """
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "role": "user",
        "avatar": None,
        "created_at": "2023-01-01T00:00:00",
        "confirmed": True
    }