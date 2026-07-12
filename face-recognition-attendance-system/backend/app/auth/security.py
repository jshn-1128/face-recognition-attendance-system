import logging
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError

from app.auth.exceptions import ExpiredTokenException, InvalidTokenException
from app.core.config import settings

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def create_access_token(
    data: dict[str, str | int | bool | list[str] | None],
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token with expiration."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta is not None
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire

    token = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    logger.info("Token created for subject: %s", data.get("sub", "unknown"))
    return token


def decode_token(token: str) -> dict[str, str | int | bool | list[str] | None]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        logger.info(
            "Token validated for subject: %s",
            payload.get("sub", "unknown"),
        )
        return payload  # type: ignore[return-value]

    except ExpiredSignatureError:
        logger.warning("Expired token attempted")
        raise ExpiredTokenException()
    except JWTError:
        logger.warning("Token decode failed", exc_info=True)
        raise InvalidTokenException()
