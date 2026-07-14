from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.exceptions import InvalidCredentialsException
from app.auth.schemas import Token, UserResponse
from app.auth.security import create_access_token, verify_password
from app.users.repository import get_user_by_email, get_user_by_id


async def login(
    db: AsyncSession,
    email: str,
    password: str,
) -> Token:
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        raise InvalidCredentialsException()

    token = create_access_token(
        data={
            "sub": str(user.id),
            "is_active": user.is_active,
            "role": user.role.value if hasattr(user.role, "value") else user.role,
        },
    )
    return Token(access_token=token, token_type="bearer")


async def get_current_user_from_db(
    db: AsyncSession,
    user_id: str,
) -> UserResponse:
    import uuid
    user = await get_user_by_id(db, uuid.UUID(user_id))
    if not user:
        raise InvalidCredentialsException()

    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
    )
