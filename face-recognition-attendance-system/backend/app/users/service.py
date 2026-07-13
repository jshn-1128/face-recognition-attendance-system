import logging
import uuid
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.exceptions import InvalidCredentialsException
from app.auth.security import create_access_token, hash_password, verify_password
from app.users.exceptions import (
    DuplicateEmployeeIdException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from app.users.models import User
from app.users.repository import (
    create_user,
    delete_user as delete_user_repo,
    exists_by_email,
    exists_by_employee_id,
    get_all_users,
    get_user_by_email,
    get_user_by_id,
    update_user as update_user_repo,
)
from app.users.schemas import UserCreate, UserUpdate

logger = logging.getLogger(__name__)


async def register_user(
    db: AsyncSession,
    request: UserCreate,
) -> User:
    if await exists_by_email(db, request.email):
        logger.warning("Duplicate registration attempt: %s", request.email)
        raise UserAlreadyExistsException()

    if request.employee_id and await exists_by_employee_id(db, request.employee_id):
        raise DuplicateEmployeeIdException()

    password_hash = hash_password(request.password)
    user = await create_user(
        db,
        full_name=request.full_name,
        email=request.email,
        password_hash=password_hash,
        employee_id=request.employee_id,
        department=request.department,
        role=request.role.value if hasattr(request.role, "value") else request.role,
    )

    logger.info("User registered: %s (%s)", user.email, user.id)
    return user


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str,
) -> tuple[User, str]:
    user = await get_user_by_email(db, email)
    if not user:
        logger.warning("Login failed: unknown email %s", email)
        raise InvalidCredentialsException()

    if not verify_password(password, user.password_hash):
        logger.warning("Login failed: wrong password for %s", email)
        raise InvalidCredentialsException()

    if not user.is_active:
        logger.warning("Login failed: inactive account %s", email)
        raise InvalidCredentialsException()

    token = create_access_token(
        data={
            "sub": str(user.id),
            "is_active": user.is_active,
            "role": user.role.value if hasattr(user.role, "value") else user.role,
        },
    )

    logger.info("User logged in: %s", user.email)
    return user, token


async def list_users(
    db: AsyncSession,
    *,
    skip: int = 0,
    limit: int = 100,
) -> tuple[Sequence[User], int]:
    return await get_all_users(db, skip=skip, limit=limit)


async def get_user(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> User:
    user = await get_user_by_id(db, user_id)
    if not user:
        raise UserNotFoundException()
    return user


async def update_user(
    db: AsyncSession,
    user_id: uuid.UUID,
    request: UserUpdate,
) -> User:
    user = await get_user_by_id(db, user_id)
    if not user:
        raise UserNotFoundException()

    if request.email is not None and request.email != user.email:
        if await exists_by_email(db, request.email):
            raise UserAlreadyExistsException()

    if request.employee_id is not None and request.employee_id != user.employee_id:
        if await exists_by_employee_id(db, request.employee_id):
            raise DuplicateEmployeeIdException()

    updated = await update_user_repo(
        db,
        user,
        full_name=request.full_name,
        email=request.email,
        employee_id=request.employee_id,
        department=request.department,
        role=request.role.value if request.role and hasattr(request.role, "value") else request.role,
        is_active=request.is_active,
    )

    logger.info("User updated: %s", user.email)
    return updated


async def delete_user(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> None:
    user = await get_user_by_id(db, user_id)
    if not user:
        raise UserNotFoundException()

    await delete_user_repo(db, user)
    logger.info("User deleted: %s (%s)", user.email, user.id)
