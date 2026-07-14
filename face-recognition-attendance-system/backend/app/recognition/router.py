"""Recognition API router.

Defines the external API contract for the recognition subsystem.
Every endpoint returns ``501 Not Implemented`` until the
recognition pipeline is connected in a later milestone.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user
from app.database.session import get_db
from app.recognition.service import RecognitionService

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
    "face.  This endpoint will be implemented in Milestone 7.4.2.",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    responses={
        501: {"description": "Not implemented — planned for Milestone 7.4.2"},
        401: {"description": "Authentication required"},
    },
)
async def recognize(
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
    service: RecognitionService = Depends(get_recognition_service),
) -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=_NOT_IMPLEMENTED["detail"],
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
