from app.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    Token,
    UserResponse,
)


def register(request: RegisterRequest) -> UserResponse:
    """Register a new user.

    Returns placeholder response — database integration pending.
    """
    return UserResponse(
        id="placeholder-uuid",
        email=request.email,
        full_name=request.full_name,
        is_active=True,
    )


def login(request: LoginRequest) -> Token:
    """Authenticate a user and return a JWT.

    Returns placeholder response — database integration pending.
    """
    return Token(
        access_token="placeholder-token",
        token_type="bearer",
    )


def refresh_token(token: str) -> Token:
    """Refresh an expired access token.

    Returns placeholder response — database integration pending.
    """
    return Token(
        access_token="refreshed-placeholder-token",
        token_type="bearer",
    )


def get_current_user(user_id: str) -> UserResponse:
    """Retrieve the currently authenticated user.

    Returns placeholder response — database integration pending.
    """
    return UserResponse(
        id=user_id,
        email="user@example.com",
        full_name="User Name",
        is_active=True,
    )
