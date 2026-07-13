from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Face Recognition Attendance API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "attendance_db"
    DATABASE_USER: str = "attendance_user"
    DATABASE_PASSWORD: str = "changeme"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    FACE_MODEL_NAME: str = "buffalo_l"
    FACE_STORAGE_PATH: str = "storage/faces"
    MAX_IMAGE_SIZE_MB: int = 10
    SUPPORTED_IMAGE_TYPES: str = "jpg,jpeg,png"

    @property
    def SUPPORTED_IMAGE_TYPES_LIST(self) -> list[str]:
        return [t.strip() for t in self.SUPPORTED_IMAGE_TYPES.split(",")]

    class Config:
        env_file = ".env"


settings = Settings()
