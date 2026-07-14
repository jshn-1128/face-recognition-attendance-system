import uuid


class RecognitionRepository:
    """Data-access layer for recognition workflows.

    Responsible for retrieving enrolled face embeddings from the
    database so the matcher can perform similarity comparisons.

    All methods raise ``NotImplementedError`` until the repository
    is implemented in a later milestone.
    """

    async def get_all_embeddings(self) -> None:
        """Retrieve all enrolled face embeddings.

        Returns:
            A list of all face embedding records in the system.

        Raises:
            NotImplementedError: Always — not yet implemented.
        """
        raise NotImplementedError("get_all_embeddings is not implemented")

    async def get_embedding_by_user(
        self,
        user_id: uuid.UUID,
    ) -> None:
        """Retrieve the face embedding for a specific user.

        Args:
            user_id: UUID of the user whose embedding is requested.

        Returns:
            The face embedding record for the given user, or ``None``.

        Raises:
            NotImplementedError: Always — not yet implemented.
        """
        raise NotImplementedError("get_embedding_by_user is not implemented")

    async def get_embedding_count(self) -> None:
        """Return the total number of enrolled face embeddings.

        Returns:
            The count of face embedding records in the database.

        Raises:
            NotImplementedError: Always — not yet implemented.
        """
        raise NotImplementedError("get_embedding_count is not implemented")
