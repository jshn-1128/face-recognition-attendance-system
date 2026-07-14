import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class RecognitionCandidate(BaseModel):
    """A single candidate returned from a recognition match.

    Represents one potential match with its similarity score and
    the associated user metadata.
    """

    user_id: uuid.UUID = Field(
        ..., description="UUID of the matched user",
    )
    confidence: float = Field(
        ..., ge=0.0, le=100.0, description="Confidence score (0–100 %)",
    )
    similarity: float = Field(
        ..., description="Raw similarity score from the matching function",
    )


class RecognitionResponse(BaseModel):
    """Recognition result returned to the API consumer.

    Encapsulates the outcome of a face recognition operation.  When
    ``matched`` is ``True`` the identity fields are populated with the
    matched user's details; when ``False`` only ``message`` is meaningful.
    """

    matched: bool = Field(
        ...,
        description="Whether a match was found above the confidence threshold",
    )
    user_id: uuid.UUID | None = Field(
        None,
        description="UUID of the matched user (``None`` when not matched)",
    )
    full_name: str | None = Field(
        None,
        description="Full name of the matched user (``None`` when not matched)",
    )
    employee_id: str | None = Field(
        None,
        description=(
            "Employee identifier of the matched user "
            "(``None`` when not matched)"
        ),
    )
    department: str | None = Field(
        None,
        description=(
            "Department of the matched user "
            "(``None`` when not matched)"
        ),
    )
    confidence: float = Field(
        0.0,
        ge=0.0,
        le=100.0,
        description="Confidence percentage (0–100 %) of the match",
    )
    similarity: float = Field(
        0.0,
        description="Raw cosine similarity score of the best match",
    )
    model_name: str | None = Field(
        None,
        description=(
            "Name of the AI model that produced the embedding "
            "(``None`` when not matched)"
        ),
    )
    message: str = Field(
        ...,
        description="Human-readable status message",
    )


class RecognitionFailure(BaseModel):
    """Failed recognition result.

    Returned when recognition could not be performed due to an
    error or invalid input.
    """

    error: str = Field(
        ..., description="Human-readable error description",
    )
    code: str = Field(
        ..., description="Machine-readable error code for programmatic handling",
    )


class RecognitionMetadata(BaseModel):
    """Metadata about the recognition operation.

    Provides information about the recognition request itself,
    separate from the match result.
    """

    model_name: str = Field(
        ..., description="Face recognition model used for matching",
    )
    total_candidates: int = Field(
        ..., ge=0, description="Number of enrolled embeddings searched",
    )
    processing_time_ms: float | None = Field(
        None, ge=0.0, description="Recognition processing time in milliseconds",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the recognition operation was performed",
    )
