import logging
import traceback

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic_core import ValidationError
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


async def general_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    logger.error("Unhandled exception: %s", str(exc))
    logger.error(traceback.format_exc())

    if isinstance(exc, SQLAlchemyError):
        logger.error("Database error: %s", str(exc))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "A database error occurred",
                "error_type": "DatabaseError",
            },
        )

    if isinstance(exc, ValidationError):
        logger.warning("Validation error: %s", str(exc))
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "Validation failed",
                "error_type": "ValidationError",
            },
        )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred",
            "error_type": type(exc).__name__,
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning("HTTP exception: %s", str(exc.detail))
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )
