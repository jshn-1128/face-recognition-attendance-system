import uuid

from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user
from app.database.session import get_db
from app.face.exceptions import InvalidImageException
from app.face.schemas import FaceRegisterResponse, FaceResponse
from app.face.service import delete_face, get_face, register_face, update_face

router = APIRouter(prefix="/faces", tags=["Faces"])


@router.post(
    "/register",
    summary="Register a face embedding",
    description="Upload a face image to register the user's face embedding. "
    "The image must contain exactly one face. Accepted formats: jpg, jpeg, png. "
    "Maximum file size: 10 MB.",
    response_model=FaceRegisterResponse,
    status_code=201,
    responses={
        400: {"description": "Invalid image, no face, multiple faces, or unsupported format"},
        409: {"description": "Face embedding already exists for this user"},
    },
)
async def register(
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
) -> FaceRegisterResponse:
    user_id = uuid.UUID(current_user["sub"])
    image_bytes = await _read_upload(file)
    return await register_face(
        db,
        user_id=user_id,
        filename=file.filename or "image.jpg",
        content_type=file.content_type,
        file_size=len(image_bytes),
        image_bytes=image_bytes,
    )


@router.get(
    "/me",
    summary="Get face embedding metadata",
    description="Returns face embedding metadata for the current user. "
    "The embedding vector is never returned.",
    response_model=FaceResponse,
    responses={
        404: {"description": "No face embedding found for this user"},
    },
)
async def get_my_face(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
) -> FaceResponse:
    user_id = uuid.UUID(current_user["sub"])
    return await get_face(db, user_id)


@router.put(
    "/me",
    summary="Replace face embedding",
    description="Replace the existing face embedding with a new one. "
    "The old image is deleted. Same validation rules as registration.",
    response_model=FaceResponse,
    responses={
        400: {"description": "Invalid image, no face, multiple faces, or unsupported format"},
        404: {"description": "No face embedding found for this user"},
    },
)
async def update_my_face(
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
) -> FaceResponse:
    user_id = uuid.UUID(current_user["sub"])
    image_bytes = await _read_upload(file)
    return await update_face(
        db,
        user_id=user_id,
        filename=file.filename or "image.jpg",
        content_type=file.content_type,
        file_size=len(image_bytes),
        image_bytes=image_bytes,
    )


@router.delete(
    "/me",
    summary="Delete face embedding",
    description="Delete the face embedding record and the stored image. "
    "Returns 204 No Content.",
    status_code=204,
    responses={
        404: {"description": "No face embedding found for this user"},
    },
)
async def delete_my_face(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
) -> None:
    user_id = uuid.UUID(current_user["sub"])
    await delete_face(db, user_id)


async def _read_upload(file: UploadFile) -> bytes:
    """Read an uploaded file, ensuring it is not empty."""
    if file.size is not None and file.size == 0:
        raise InvalidImageException("Uploaded file is empty")
    image_bytes = await file.read()
    if not image_bytes:
        raise InvalidImageException("Uploaded file is empty")
    return image_bytes
