import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.users.models import UserRole


class UserCreate(BaseModel):
    email: str = Field(
        ..., example="user@example.com", description="User email address"
    )
    password: str = Field(
        ...,
        min_length=8,
        example="strongpassword123",
        description="User password (min 8 characters)",
    )
    full_name: str = Field(
        ...,
        min_length=1,
        example="John Doe",
        description="User full name",
    )
    employee_id: str | None = Field(
        None, example="EMP001", description="Employee identifier"
    )
    department: str | None = Field(
        None, example="Engineering", description="Department name"
    )
    role: UserRole = Field(
        default=UserRole.EMPLOYEE, description="User role"
    )


class UserUpdate(BaseModel):
    full_name: str | None = Field(
        None, example="John Updated", description="Updated full name"
    )
    email: str | None = Field(
        None, example="updated@example.com", description="Updated email"
    )
    employee_id: str | None = Field(
        None, example="EMP002", description="Updated employee ID"
    )
    department: str | None = Field(
        None, example="Product", description="Updated department"
    )
    role: UserRole | None = Field(
        None, description="Updated user role"
    )
    is_active: bool | None = Field(
        None, description="Whether the user account is active"
    )


class UserResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Unique user identifier")
    full_name: str = Field(..., description="User full name")
    email: str = Field(..., description="User email address")
    employee_id: str | None = Field(None, description="Employee identifier")
    department: str | None = Field(None, description="Department name")
    role: UserRole = Field(..., description="User role")
    is_active: bool = Field(..., description="Whether the user is active")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int = Field(..., description="Total number of users")


class UserPublic(BaseModel):
    id: uuid.UUID = Field(..., description="Unique user identifier")
    full_name: str = Field(..., description="User full name")
    email: str = Field(..., description="User email address")
    role: UserRole = Field(..., description="User role")
    is_active: bool = Field(..., description="Whether the user is active")

    model_config = {"from_attributes": True}
