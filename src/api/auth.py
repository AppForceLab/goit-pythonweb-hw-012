import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
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
from src.services.email import send_verification_email
from src.services.redis_client import get_redis

router = APIRouter(tags=["Auth"])


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(body: UserCreate, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == body.email)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=409, detail="User with this email already exists"
        )

    hashed_password = pwd_context.hash(body.password)
    verification_token = str(uuid.uuid4())

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
    await send_verification_email(user.email, verification_token)
    return user


@router.post("/login", response_model=Token)
async def login(user: UserCreate, db: AsyncSession = Depends(get_db)):
    valid_user = await handlers.authenticate_user(user.email, user.password, db)
    token_data = {"sub": str(valid_user.email)}
    return {
        "access_token": create_access_token(token_data),
        "refresh_token": create_refresh_token(token_data),
    }


@router.get("/verify/{token}")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.verification_token == token)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Invalid verification token")

    user.confirmed = True
    user.verification_token = None
    await db.commit()

    return {"message": "Email verified successfully"}


@router.get("/me")
@limiter.limit("5/minute")
async def read_me(request: Request, current_user: User = Depends(get_current_user)):
    return {"email": current_user.email, "username": current_user.username}


@router.post("/refresh", response_model=Token)
async def get_refresh_token(request: Request, db: AsyncSession = Depends(get_db)):
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
async def update_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400, detail="Invalid file type. Only images are allowed."
        )

    avatar_url = await upload_avatar(file)
    current_user.avatar = avatar_url
    await db.commit()
    return {"avatar_url": avatar_url}
