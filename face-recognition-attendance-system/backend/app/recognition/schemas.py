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
    """Successful recognition result.

    Returned when a face is successfully matched to an enrolled user.
    """

    recognized: bool = Field(
        ..., description="Whether a match was found above the confidence threshold",
    )
    user_id: uuid.UUID | None = Field(
        None, description="UUID of the matched user, if recognised",
    )
    confidence: float | None = Field(
        None, ge=0.0, le=100.0, description="Confidence score of the match",
    )
    candidates: list[RecognitionCandidate] = Field(
        default_factory=list,
        description="Top matching candidates, sorted by confidence descending",
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
