import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import SecurityUtils, get_db
from app.schemas.user import TokenResponse, UserCreate, UserLogin
from app.services.user_service import UserService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    logger.info("Registration attempt for email: %s", user_data.email)

    existing_user = UserService.get_user_by_email(db, user_data.email)
    if existing_user:
        logger.warning(
            "Registration failed: Email already exists: %s", user_data.email
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    existing_username = UserService.get_user_by_username(db, user_data.username)
    if existing_username:
        logger.warning(
            "Registration failed: Username already exists: %s", user_data.username
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    user = UserService.create_user(db, user_data)
    logger.info("User registered successfully: %s", user.email)

    access_token_expires = timedelta(minutes=30)
    access_token = SecurityUtils.create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    logger.info("Login attempt for email: %s", credentials.email)

    user = UserService.get_user_by_email(db, credentials.email)

    if not user or not SecurityUtils.verify_password(
        credentials.password,
        user.hashed_password,
    ):
        logger.warning(
            "Login failed: Invalid credentials for email: %s", credentials.email
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        logger.warning("Login failed: Inactive user: %s", credentials.email)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    logger.info("User logged in successfully: %s", user.email)

    access_token_expires = timedelta(minutes=30)
    access_token = SecurityUtils.create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }
