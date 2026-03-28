import logging

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import SecurityUtils
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

logger = logging.getLogger(__name__)


class UserService:
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        hashed_password = SecurityUtils.hash_password(user_data.password)

        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            role="USER",
            is_active=True,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        logger.info("User created: %s - %s", user.id, user.email)
        return user

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> User:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_all_users(db: Session) -> list:
        return db.query(User).all()

    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> User:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            return None

        if user_update.username:
            user.username = user_update.username

        if user_update.email:
            user.email = user_update.email

        db.commit()
        db.refresh(user)

        logger.info("User updated: %s", user_id)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            return False

        db.delete(user)
        db.commit()

        logger.info("User deleted: %s", user_id)
        return True

    @staticmethod
    def count_users(db: Session) -> int:
        return db.query(func.count(User.id)).scalar()
