from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-grade AI-powered attendance system using face recognition technology.",
)


@app.get("/")
async def root():
    return {
        "message": "Face Recognition Attendance System API",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
