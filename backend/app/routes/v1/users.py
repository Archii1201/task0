import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_admin_user, get_current_user, get_db
from app.models.user import User
from app.schemas.user import MessageResponse, UserResponse, UserUpdate
from app.services.user_service import UserService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    logger.info("Current user info requested: %s", current_user.email)
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logger.info("User info requested for ID: %s", user_id)

    if current_user.role != "ADMIN" and current_user.id != user_id:
        logger.warning(
            "Unauthorized access attempt by user %s to user %s",
            current_user.id,
            user_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user",
        )

    user = UserService.get_user_by_id(db, user_id)
    if not user:
        logger.warning("User not found: %s", user_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.put("/me/profile", response_model=UserResponse)
async def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logger.info("Profile update requested by user: %s", current_user.email)

    user = UserService.update_user(db, current_user.id, user_update)
    logger.info("Profile updated for user: %s", current_user.email)

    return user


@router.get("", response_model=list[UserResponse])
async def list_users(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    logger.info("All users list requested by admin: %s", current_user.email)
    return UserService.get_all_users(db)


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    logger.info(
        "User deletion requested by admin %s for user %s",
        current_user.id,
        user_id,
    )

    user = UserService.get_user_by_id(db, user_id)
    if not user:
        logger.warning("User not found for deletion: %s", user_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    UserService.delete_user(db, user_id)
    logger.info("User deleted by admin: %s", user_id)

    return {"message": "User deleted successfully"}
