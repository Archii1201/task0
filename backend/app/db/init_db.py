import logging

from app.core.security import SecurityUtils
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.task import Task  # noqa: F401
from app.models.user import User

logger = logging.getLogger(__name__)


def init_db():
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")

    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.email == "admin@example.com").first()

        if not admin_user:
            admin_user = User(
                email="admin@example.com",
                username="admin",
                hashed_password=SecurityUtils.hash_password("admin123"),
                role="ADMIN",
                is_active=True,
            )
            db.add(admin_user)
            logger.info("Admin user created: admin@example.com")

        sample_user = db.query(User).filter(User.email == "user@example.com").first()

        if not sample_user:
            sample_user = User(
                email="user@example.com",
                username="testuser",
                hashed_password=SecurityUtils.hash_password("user123"),
                role="USER",
                is_active=True,
            )
            db.add(sample_user)
            logger.info("Sample user created: user@example.com")

        db.commit()
        logger.info("Database initialization completed")

    except Exception as e:
        logger.error("Error initializing database: %s", str(e))
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
