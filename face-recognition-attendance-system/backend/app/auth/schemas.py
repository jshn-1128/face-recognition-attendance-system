from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    email: str = Field(
        ..., example="user@example.com", description="User email address"
    )
    password: str = Field(
        ..., min_length=8, example="strongpassword123", description="User password (min 8 characters)"
    )
    full_name: str = Field(
        ..., example="John Doe", description="User full name"
    )


class LoginRequest(BaseModel):
    email: str = Field(
        ..., example="user@example.com", description="Registered email address"
    )
    password: str = Field(
        ..., example="strongpassword123", description="Account password"
    )


class Token(BaseModel):
    access_token: str = Field(
        ..., description="JWT access token"
    )
    token_type: str = Field(
        default="bearer", description="Token type"
    )


class TokenPayload(BaseModel):
    sub: str | None = Field(None, description="Subject identifier (user ID)")
    exp: int | None = Field(None, description="Token expiration timestamp")


class UserResponse(BaseModel):
    id: str = Field(..., example="uuid-string", description="Unique user identifier")
    email: str = Field(..., example="user@example.com", description="User email")
    full_name: str = Field(..., example="John Doe", description="User full name")
    is_active: bool = Field(default=True, description="Whether the user account is active")


class RefreshRequest(BaseModel):
    token: str = Field(..., description="Valid JWT access token to refresh")


class MessageResponse(BaseModel):
    message: str = Field(..., description="Response message")
