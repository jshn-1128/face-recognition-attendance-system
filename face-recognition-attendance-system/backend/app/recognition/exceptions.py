from fastapi import HTTPException, status


class RecognitionException(HTTPException):
    """Base exception for all recognition-related errors."""

    def __init__(
        self,
        detail: str = "Recognition error",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail)


class RecognitionFailedException(RecognitionException):
    """Raised when the recognition process encounters an error."""

    def __init__(self) -> None:
        super().__init__(
            detail="Face recognition failed",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class UnknownPersonException(RecognitionException):
    """Raised when the face does not match any enrolled user."""

    def __init__(self) -> None:
        super().__init__(
            detail="Face did not match any enrolled user",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class RecognitionThresholdException(RecognitionException):
    """Raised when the best match is below the confidence threshold."""

    def __init__(self) -> None:
        super().__init__(
            detail="Recognition confidence below threshold",
            status_code=status.HTTP_200_OK,
        )


class RecognitionModelException(RecognitionException):
    """Raised when the recognition model is unavailable or fails to load."""

    def __init__(self) -> None:
        super().__init__(
            detail="Recognition model is not available",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class NoEmbeddingsException(RecognitionException):
    """Raised when no face embeddings exist in the database."""

    def __init__(self) -> None:
        super().__init__(
            detail="No face embeddings found in the system. "
            "Users must register their face first",
            status_code=status.HTTP_404_NOT_FOUND,
        )
