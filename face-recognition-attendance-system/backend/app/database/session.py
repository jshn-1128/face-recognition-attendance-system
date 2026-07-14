from collections.abc import AsyncGenerator, Callable
import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.database.connection import engine

logger = logging.getLogger(__name__)

AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


def _add_commit_hook(session: AsyncSession, hook: Callable[[], None]) -> None:
    if "_commit_hooks" not in session.info:
        session.info["_commit_hooks"] = []
    session.info["_commit_hooks"].append(hook)


def _add_rollback_hook(session: AsyncSession, hook: Callable[[], None]) -> None:
    if "_rollback_hooks" not in session.info:
        session.info["_rollback_hooks"] = []
    session.info["_rollback_hooks"].append(hook)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        session.info["_commit_hooks"] = []
        session.info["_rollback_hooks"] = []
        try:
            yield session
            await session.commit()
            for hook in session.info["_commit_hooks"]:
                try:
                    hook()
                except Exception:
                    logger.exception("Commit hook failed")
        except Exception:
            await session.rollback()
            for hook in session.info["_rollback_hooks"]:
                try:
                    hook()
                except Exception:
                    logger.exception("Rollback hook failed")
            raise
