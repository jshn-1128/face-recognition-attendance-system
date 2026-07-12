from fastapi import HTTPException, status


class AuthException(HTTPException):
    """Base authentication exception."""

    def __init__(
        self,
        detail: str = "Authentication error",
        status_code: int = status.HTTP_401_UNAUTHORIZED,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail)


class InvalidCredentialsException(AuthException):
    def __init__(self) -> None:
        super().__init__(
            detail="Invalid email or password",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class InvalidTokenException(AuthException):
    def __init__(self) -> None:
        super().__init__(
            detail="Invalid or malformed token",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class ExpiredTokenException(AuthException):
    def __init__(self) -> None:
        super().__init__(
            detail="Token has expired",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class UnauthorizedException(AuthException):
    def __init__(self, detail: str = "Not authorized") -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_403_FORBIDDEN,
        )
