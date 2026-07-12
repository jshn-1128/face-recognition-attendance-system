from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.core.config import settings


def create_engine() -> AsyncEngine:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
    )
    return engine


engine = create_engine()
