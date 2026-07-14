import uuid

from sqlalchemy.ext.asyncio import AsyncSession


class RecognitionService:
    """Orchestrates face recognition workflows.

    This service is responsible for:
        - Accepting an uploaded face image and identifying the person.
        - Matching a pre-computed embedding against enrolled embeddings.
        - Validating recognition requests before processing.

    All methods raise ``NotImplementedError`` until the recognition
    engine is implemented in a later milestone.
    """

    async def identify_face(
        self,
        db: AsyncSession,
        image_bytes: bytes,
    ) -> None:
        """Identify a person from a face image.

        Args:
            db: Active database session.
            image_bytes: Raw bytes of the uploaded face image.

        Raises:
            NotImplementedError: Always — not yet implemented.
        """
        raise NotImplementedError("identify_face is not implemented")

    async def recognize_embedding(
        self,
        db: AsyncSession,
        embedding: list[float],
    ) -> None:
        """Match a face embedding against all enrolled embeddings.

        Args:
            db: Active database session.
            embedding: A 512-dimensional face embedding vector.

        Raises:
            NotImplementedError: Always — not yet implemented.
        """
        raise NotImplementedError("recognize_embedding is not implemented")

    async def validate_recognition_request(
        self,
        user_id: uuid.UUID,
    ) -> None:
        """Validate that a user is eligible for recognition.

        Args:
            user_id: UUID of the user requesting recognition.

        Raises:
            NotImplementedError: Always — not yet implemented.
        """
        raise NotImplementedError("validate_recognition_request is not implemented")
