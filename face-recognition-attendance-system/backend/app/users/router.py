import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user
from app.database.session import get_db
from app.users.schemas import (
    UserCreate,
    UserListResponse,
    UserResponse,
    UserUpdate,
)
from app.users.service import (
    delete_user,
    get_user,
    list_users,
    register_user,
    update_user,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/",
    summary="Create a new user",
    description="Register a new user in the system.",
    response_model=UserResponse,
    status_code=201,
)
async def create_user(
    request: UserCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_active_user),
) -> UserResponse:
    user = await register_user(db, request)
    return UserResponse.model_validate(user)


@router.get(
    "/",
    summary="List all users",
    description="Retrieve a paginated list of all registered users.",
    response_model=UserListResponse,
    status_code=200,
)
async def list_all_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_active_user),
) -> UserListResponse:
    users, total = await list_users(db, skip=skip, limit=limit)
    return UserListResponse(
        users=[UserResponse.model_validate(u) for u in users],
        total=total,
    )


@router.get(
    "/{user_id}",
    summary="Get user by ID",
    description="Retrieve a single user by their UUID.",
    response_model=UserResponse,
    status_code=200,
)
async def get_user_by_id(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_active_user),
) -> UserResponse:
    user = await get_user(db, user_id)
    return UserResponse.model_validate(user)


@router.put(
    "/{user_id}",
    summary="Update a user",
    description="Update an existing user's information.",
    response_model=UserResponse,
    status_code=200,
)
async def update_user_by_id(
    user_id: uuid.UUID,
    request: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_active_user),
) -> UserResponse:
    user = await update_user(db, user_id, request)
    return UserResponse.model_validate(user)


@router.delete(
    "/{user_id}",
    summary="Delete a user",
    description="Permanently remove a user from the system.",
    status_code=204,
)
async def delete_user_by_id(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_active_user),
) -> None:
    await delete_user(db, user_id)
