import uuid

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.exceptions import InvalidTokenException, UnauthorizedException
from app.auth.security import decode_token
from app.database.session import get_db
from app.users.repository import get_user_by_id

oauth2_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(oauth2_scheme),
) -> dict[str, str | int | bool | list[str] | None]:
    """Validate the JWT signature and return the token payload.

    This only verifies the cryptographic integrity of the token.
    Authorization (is_active, user existence) is checked by
    ``get_current_active_user`` against the database.
    """
    if credentials is None:
        raise InvalidTokenException()

    payload = decode_token(credentials.credentials)
    return payload


async def get_current_active_user(
    current_user: dict[str, str | int | bool | list[str] | None] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str | int | bool | list[str] | None]:
    """Return the current user if the account exists and is active.

    Loads the user from the database on every request — never trusts
    cached ``is_active`` state inside the JWT.
    """
    user_id = current_user.get("sub")
    if not user_id:
        raise InvalidTokenException(detail="Token missing subject claim")

    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        raise InvalidTokenException(detail="Invalid user identifier in token")

    user = await get_user_by_id(db, uid)
    if not user:
        raise InvalidTokenException(detail="User not found")

    if not user.is_active:
        raise UnauthorizedException(detail="Inactive user account")

    return {
        "sub": str(user.id),
        "is_active": user.is_active,
        "role": user.role.value if hasattr(user.role, "value") else user.role,
    }
