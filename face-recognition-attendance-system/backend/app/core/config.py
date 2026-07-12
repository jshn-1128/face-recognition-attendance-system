from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Face Recognition Attendance API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
