from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Face Recognition Attendance API"
    DEBUG: bool = False
    DATABASE_URL: str = "postgresql+asyncpg://attendance_user:changeme@localhost:5432/attendance_db"
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"


settings = Settings()
