import logging

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate

logger = logging.getLogger(__name__)


class TaskService:
    @staticmethod
    def create_task(db: Session, task_data: TaskCreate, user_id: int) -> Task:
        task = Task(
            title=task_data.title,
            description=task_data.description,
            status=task_data.status,
            owner_id=user_id,
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        logger.info("Task created: %s - %s", task.id, task.title)
        return task

    @staticmethod
    def get_task(db: Session, task_id: int) -> Task:
        return db.query(Task).filter(Task.id == task_id).first()

    @staticmethod
    def get_user_tasks(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
        status: str = None,
    ) -> tuple:
        query = db.query(Task).filter(Task.owner_id == user_id)

        if status:
            query = query.filter(Task.status == status)

        total = query.count()
        tasks = query.offset(skip).limit(limit).all()

        return tasks, total

    @staticmethod
    def update_task(db: Session, task_id: int, task_update: TaskUpdate) -> Task:
        task = db.query(Task).filter(Task.id == task_id).first()

        if not task:
            return None

        if task_update.title:
            task.title = task_update.title

        if task_update.description is not None:
            task.description = task_update.description

        if task_update.status:
            task.status = task_update.status

        if task_update.is_completed is not None:
            task.is_completed = task_update.is_completed

        db.commit()
        db.refresh(task)

        logger.info("Task updated: %s", task_id)
        return task

    @staticmethod
    def delete_task(db: Session, task_id: int) -> bool:
        task = db.query(Task).filter(Task.id == task_id).first()

        if not task:
            return False

        db.delete(task)
        db.commit()

        logger.info("Task deleted: %s", task_id)
        return True

    @staticmethod
    def get_all_tasks(
        db: Session,
        skip: int = 0,
        limit: int = 10,
    ) -> tuple:
        total = db.query(func.count(Task.id)).scalar()
        tasks = db.query(Task).offset(skip).limit(limit).all()

        return tasks, total

    @staticmethod
    def count_tasks(db: Session, user_id: int) -> int:
        return (
            db.query(func.count(Task.id)).filter(Task.owner_id == user_id).scalar()
        )
