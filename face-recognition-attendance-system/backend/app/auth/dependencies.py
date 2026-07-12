from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.exceptions import InvalidTokenException, UnauthorizedException
from app.auth.security import decode_token

oauth2_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(oauth2_scheme),
) -> dict[str, str | int | bool | list[str] | None]:
    """Validate the JWT and return the current user's token payload."""
    if credentials is None:
        raise InvalidTokenException()

    payload = decode_token(credentials.credentials)
    return payload


def get_current_active_user(
    current_user: dict[str, str | int | bool | list[str] | None] = Depends(get_current_user),
) -> dict[str, str | int | bool | list[str] | None]:
    """Return the current user if the account is active."""
    is_active = current_user.get("is_active", True)
    if not is_active:
        raise UnauthorizedException(detail="Inactive user account")
    return current_user
