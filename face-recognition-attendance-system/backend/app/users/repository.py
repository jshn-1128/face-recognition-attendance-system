import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.models import User


async def create_user(
    db: AsyncSession,
    *,
    full_name: str,
    email: str,
    password_hash: str,
    employee_id: str | None = None,
    department: str | None = None,
    role: str = "employee",
    is_active: bool = True,
) -> User:
    user = User(
        full_name=full_name,
        email=email,
        password_hash=password_hash,
        employee_id=employee_id,
        department=department,
        role=role,
        is_active=is_active,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def get_all_users(
    db: AsyncSession,
    *,
    skip: int = 0,
    limit: int = 100,
) -> tuple[Sequence[User], int]:
    count_result = await db.execute(select(User))
    total = len(count_result.scalars().all())

    result = await db.execute(
        select(User).offset(skip).limit(limit)
    )
    users = result.scalars().all()
    return users, total


async def update_user(
    db: AsyncSession,
    user: User,
    **kwargs: str | int | bool | None,
) -> User:
    for key, value in kwargs.items():
        if value is not None and hasattr(user, key):
            setattr(user, key, value)
    await db.flush()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user: User) -> None:
    await db.delete(user)
    await db.flush()


async def exists_by_email(db: AsyncSession, email: str) -> bool:
    result = await db.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none() is not None


async def exists_by_employee_id(db: AsyncSession, employee_id: str) -> bool:
    result = await db.execute(
        select(User).where(User.employee_id == employee_id)
    )
    return result.scalar_one_or_none() is not None
