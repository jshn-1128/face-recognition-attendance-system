import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.face.models import FaceEmbedding


async def create_embedding(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    embedding: list[float],
    model_name: str,
    image_path: str,
) -> FaceEmbedding:
    record = FaceEmbedding(
        user_id=user_id,
        embedding=embedding,
        model_name=model_name,
        image_path=image_path,
    )
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


async def get_embedding_by_user(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> FaceEmbedding | None:
    result = await db.execute(
        select(FaceEmbedding).where(FaceEmbedding.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def update_embedding(
    db: AsyncSession,
    record: FaceEmbedding,
    **kwargs: str | list[float] | None,
) -> FaceEmbedding:
    for key, value in kwargs.items():
        if value is not None and hasattr(record, key):
            setattr(record, key, value)
    await db.flush()
    await db.refresh(record)
    return record


async def delete_embedding(
    db: AsyncSession,
    record: FaceEmbedding,
) -> None:
    await db.delete(record)
    await db.flush()


async def embedding_exists(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> bool:
    result = await db.execute(
        select(FaceEmbedding).where(FaceEmbedding.user_id == user_id)
    )
    return result.scalar_one_or_none() is not None
