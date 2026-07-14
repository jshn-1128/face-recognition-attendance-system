"""Recognition API router.

Defines the external API contract for the recognition subsystem.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user
from app.database.session import get_db
from app.face.exceptions import (
    FaceModelException,
    FaceNotFoundException,
    InvalidImageException,
    MultipleFacesDetectedException,
    UnsupportedImageException,
)
from app.face.service import extract_embedding
from app.recognition.schemas import RecognitionResponse
from app.recognition.service import RecognitionService, RecognitionServiceError

router = APIRouter(
    prefix="/recognition",
    tags=["Recognition"],
)


# ---------------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------------


async def get_recognition_service() -> RecognitionService:
    """Provider for the :class:`RecognitionService`.

    Returns a new stateless service instance per request.  The service
    internally defaults to :class:`RecognitionRepository` when no
    repository is explicitly injected.
    """
    return RecognitionService()


_NOT_IMPLEMENTED = {
    "detail": "Recognition endpoint will be implemented in Milestone 7.4.2.",
}


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/recognize",
    summary="Recognise a person from a face image",
    description="Upload a face image (jpg, jpeg, png) and receive the "
    "recognised user's identity.  The image must contain exactly one "
    "face.\n\n"
    "**Workflow:**\n"
    "1. Validates the uploaded image (MIME type, extension, size, content).\n"
    "2. Detects exactly one face and generates a 512-dimensional embedding.\n"
    "3. Matches the embedding against all enrolled faces.\n"
    "4. Returns the matched identity or a no-match response.",
    response_model=RecognitionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Recognition completed (matched or not matched)",
            "model": RecognitionResponse,
        },
        400: {
            "description": "Invalid image, unsupported format, multiple faces, corrupted or empty upload",
        },
        401: {"description": "Authentication required"},
        404: {"description": "No face detected in the uploaded image"},
        500: {"description": "Recognition service error"},
    },
)
async def recognize(
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
    service: RecognitionService = Depends(get_recognition_service),
) -> RecognitionResponse:
    """Perform one-to-many face recognition against all enrolled users.

    The endpoint is fully stateless — no database writes, no attendance
    recording.  It delegates image processing to the Face module and
    identity matching to the Recognition service.
    """
    image_bytes = await _read_upload(file)

    try:
        embedding = await extract_embedding(
            filename=file.filename or "image.jpg",
            content_type=file.content_type,
            file_size=len(image_bytes),
            image_bytes=image_bytes,
        )
    except (
        InvalidImageException,
        UnsupportedImageException,
        FaceNotFoundException,
        MultipleFacesDetectedException,
        FaceModelException,
    ):
        raise

    try:
        result = await service.recognize(db=db, query_embedding=embedding)
    except RecognitionServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )

    if not result.matched:
        return RecognitionResponse(
            matched=False,
            message="No matching face found.",
        )

    return RecognitionResponse(
        matched=True,
        user_id=result.user_id,
        full_name=result.full_name,
        employee_id=result.employee_id,
        department=result.department,
        confidence=result.confidence,
        similarity=result.similarity,
        model_name=result.model_name,
        message="Recognition successful.",
    )


@router.get(
    "/health",
    summary="Recognition subsystem health check",
    description="Returns the operational status of the recognition "
    "subsystem, including model availability and component readiness. "
    "This endpoint will be implemented in Milestone 7.4.2.",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    responses={
        501: {"description": "Not implemented — planned for Milestone 7.4.2"},
        401: {"description": "Authentication required"},
    },
)
async def health(
    current_user: dict = Depends(get_current_active_user),
) -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=_NOT_IMPLEMENTED["detail"],
    )


@router.get(
    "/stats",
    summary="Recognition statistics",
    description="Returns aggregate statistics for the recognition "
    "subsystem, such as total recognitions, success rate, and "
    "average confidence.  This endpoint will be implemented in "
    "Milestone 7.4.2.",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    responses={
        501: {"description": "Not implemented — planned for Milestone 7.4.2"},
        401: {"description": "Authentication required"},
    },
)
async def stats(
    current_user: dict = Depends(get_current_active_user),
) -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=_NOT_IMPLEMENTED["detail"],
    )


@router.post(
    "/verify",
    summary="Verify a person against a claimed identity",
    description="Upload a face image and provide a user identifier to "
    "perform one-to-one verification.  Returns whether the face matches "
    "the claimed user's registered embedding.  This endpoint will be "
    "implemented in Milestone 7.4.2.",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    responses={
        501: {"description": "Not implemented — planned for Milestone 7.4.2"},
        401: {"description": "Authentication required"},
    },
)
async def verify(
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
    service: RecognitionService = Depends(get_recognition_service),
) -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=_NOT_IMPLEMENTED["detail"],
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


async def _read_upload(file: UploadFile) -> bytes:
    """Read and validate an uploaded file, ensuring it is not empty.

    Args:
        file: The uploaded file from the request.

    Returns:
        Raw file bytes.

    Raises:
        InvalidImageException: If the file is empty.
    """
    if file.size is not None and file.size == 0:
        raise InvalidImageException("Uploaded file is empty")
    image_bytes = await file.read()
    if not image_bytes:
        raise InvalidImageException("Uploaded file is empty")
    return image_bytes
