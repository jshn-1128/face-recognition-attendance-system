import logging

from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import setup_logging
from app.database.session import AsyncSessionFactory

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-grade AI-powered attendance system using face recognition technology.",
)


@app.on_event("startup")
async def startup() -> None:
    setup_logging()
    await check_database_connection()


async def check_database_connection() -> None:
    try:
        session: AsyncSession
        async with AsyncSessionFactory() as session:
            await session.execute(text("SELECT 1"))
        logger.info("Database Connected Successfully")
    except Exception as e:
        logger.error("Database connection failed: %s", e)


@app.get("/")
async def root():
    return {
        "message": "Face Recognition Attendance System API",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    database_status = "disconnected"
    try:
        async with AsyncSessionFactory() as session:
            await session.execute(text("SELECT 1"))
        database_status = "connected"
    except Exception:
        pass

    overall = "healthy" if database_status == "connected" else "unhealthy"

    return {
        "status": overall,
        "database": database_status,
    }
