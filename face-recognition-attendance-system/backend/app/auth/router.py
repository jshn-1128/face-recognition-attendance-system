from fastapi import APIRouter, Depends

from app.auth import service
from app.auth.dependencies import get_current_active_user
from app.auth.schemas import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    Token,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    summary="Register a new user",
    description="Create a new user account with email and password.",
    response_model=UserResponse,
    status_code=201,
)
async def register(request: RegisterRequest) -> UserResponse:
    return service.register(request)


@router.post(
    "/login",
    summary="Authenticate and obtain a JWT",
    description="Exchange valid credentials for a signed JWT access token.",
    response_model=Token,
    status_code=200,
)
async def login(request: LoginRequest) -> Token:
    return service.login(request)


@router.post(
    "/refresh",
    summary="Refresh an access token",
    description="Obtain a new access token using a valid existing token.",
    response_model=Token,
    status_code=200,
)
async def refresh(request: RefreshRequest) -> Token:
    return service.refresh_token(request.token)


@router.get(
    "/me",
    summary="Get current user profile",
    description="Return the profile of the currently authenticated user.",
    response_model=UserResponse,
    status_code=200,
)
async def me(
    current_user: dict = Depends(get_current_active_user),
) -> UserResponse:
    user_id = str(current_user.get("sub", "unknown"))
    return service.get_current_user(user_id)
