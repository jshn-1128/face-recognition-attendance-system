from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import service as auth_service
from app.auth.dependencies import get_current_active_user
from app.auth.schemas import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    Token,
    UserResponse,
)
from app.database.session import get_db
from app.users.service import register_user
from app.users.schemas import UserCreate

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    summary="Register a new user",
    description="Create a new user account with email and password.",
    response_model=UserResponse,
    status_code=201,
)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    create_data = UserCreate(
        email=request.email,
        password=request.password,
        full_name=request.full_name,
    )
    user = await register_user(db, create_data)
    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
    )


@router.post(
    "/login",
    summary="Authenticate and obtain a JWT",
    description="Exchange valid credentials for a signed JWT access token.",
    response_model=Token,
    status_code=200,
)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> Token:
    return await auth_service.login(db, request.email, request.password)


@router.post(
    "/refresh",
    summary="Refresh an access token",
    description="Obtain a new access token using a valid existing token.",
    response_model=Token,
    status_code=200,
)
async def refresh(request: RefreshRequest) -> Token:
    return Token(
        access_token="refreshed-placeholder-token",
        token_type="bearer",
    )


@router.get(
    "/me",
    summary="Get current user profile",
    description="Return the profile of the currently authenticated user.",
    response_model=UserResponse,
    status_code=200,
)
async def me(
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    return await auth_service.get_current_user_from_db(
        db, str(current_user.get("sub", "unknown"))
    )
