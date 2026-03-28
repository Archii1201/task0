import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user, get_db
from app.models.user import User
from app.schemas.task import TaskCreate, TaskListResponse, TaskResponse, TaskUpdate
from app.services.task_service import TaskService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logger.info("Task creation requested by user: %s", current_user.email)

    task = TaskService.create_task(db, task_data, current_user.id)
    logger.info("Task created: %s by user %s", task.id, current_user.id)

    return task


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status_filter: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logger.info("Tasks list requested by user: %s", current_user.email)

    tasks, total = TaskService.get_user_tasks(
        db,
        current_user.id,
        skip=skip,
        limit=limit,
        status=status_filter,
    )

    return {"total": total, "tasks": tasks}


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logger.info("Task %s requested by user: %s", task_id, current_user.email)

    task = TaskService.get_task(db, task_id)

    if not task:
        logger.warning("Task not found: %s", task_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if task.owner_id != current_user.id and current_user.role != "ADMIN":
        logger.warning(
            "Unauthorized access to task %s by user %s",
            task_id,
            current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this task",
        )

    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logger.info("Task %s update requested by user: %s", task_id, current_user.email)

    task = TaskService.get_task(db, task_id)

    if not task:
        logger.warning("Task not found for update: %s", task_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if task.owner_id != current_user.id and current_user.role != "ADMIN":
        logger.warning(
            "Unauthorized update attempt for task %s by user %s",
            task_id,
            current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this task",
        )

    updated_task = TaskService.update_task(db, task_id, task_update)
    logger.info("Task updated: %s by user %s", task_id, current_user.id)

    return updated_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logger.info("Task %s deletion requested by user: %s", task_id, current_user.email)

    task = TaskService.get_task(db, task_id)

    if not task:
        logger.warning("Task not found for deletion: %s", task_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if task.owner_id != current_user.id and current_user.role != "ADMIN":
        logger.warning(
            "Unauthorized deletion attempt for task %s by user %s",
            task_id,
            current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this task",
        )

    TaskService.delete_task(db, task_id)
    logger.info("Task deleted: %s by user %s", task_id, current_user.id)

    return None
