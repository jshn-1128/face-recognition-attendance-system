"""Repository for enrolled face embeddings.

Provides data access to face embeddings joined with user profile
data for the recognition pipeline.  Returns immutable domain objects
to maintain a strict separation between the database and business
logic.
"""

import logging
import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import numpy as np
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.face.models import FaceEmbedding
from app.users.models import User

logger = logging.getLogger(__name__)


# ======================================================================
# Domain model
# ======================================================================


@dataclass(frozen=True)
class StoredEmbedding:
    """Immutable representation of an enrolled face embedding with
    associated user metadata.
    """

    user_id: uuid.UUID
    full_name: str
    employee_id: str | None
    department: str | None
    model_name: str
    embedding: list[float]
    created_at: datetime
    updated_at: datetime


# ======================================================================
# Repository-level exceptions
#
# These are deliberately **not** HTTP exceptions — the repository layer
# is below the service layer and must not depend on FastAPI.
# ======================================================================


class RepositoryError(Exception):
    """Base exception for all repository-level errors."""


class EmbeddingNotFound(RepositoryError):
    """Raised when no embedding is found for a given user identifier."""


class InvalidEmbeddingRecord(RepositoryError):
    """Raised when a stored embedding record is corrupt or fails
    validation (missing data, wrong dimensions, etc.).
    """


# ======================================================================
# Repository
# ======================================================================


class RecognitionRepository:
    """Data-access layer for recognition workflows.

    Retrieves enrolled face embeddings from the database and maps them
    to immutable :class:`StoredEmbedding` domain objects.  Every public
    method requires an explicit async database session — no sessions
    are managed internally.
    """

    # Columns fetched in every multi-row query to avoid ``SELECT *``
    # on the User table (which carries password_hash etc.).  The
    # ``embedding_*`` labels disambiguate columns with the same name
    # across the two joined tables.
    _SELECT_COLUMNS: tuple[Any, ...] = (
        User.id,
        User.full_name,
        User.employee_id,
        User.department,
        FaceEmbedding.embedding,
        FaceEmbedding.model_name,
        FaceEmbedding.created_at.label("embedding_created_at"),
        FaceEmbedding.updated_at.label("embedding_updated_at"),
    )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def get_all_embeddings(
        self,
        db: AsyncSession,
    ) -> Sequence[StoredEmbedding]:
        """Return every valid enrolled face embedding.

        Performs a single JOIN query and filters out inactive users,
        users without an embedding, and corrupt/invalid embedding
        records (wrong dimensions, NULL values, etc.).

        Args:
            db: Active async database session.

        Returns:
            A sequence of valid :class:`StoredEmbedding` instances.

        Raises:
            RepositoryError: On unexpected database errors.

        Complexity: O(N) on the number of enrolled (active) users.
        """
        return await self._fetch_embeddings(db)

    async def get_embedding_by_user_id(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> StoredEmbedding:
        """Return the embedding for a specific user.

        Args:
            db: Active async database session.
            user_id: UUID of the user whose embedding is requested.

        Returns:
            The matching :class:`StoredEmbedding`.

        Raises:
            EmbeddingNotFound: When the user does not exist, is
                inactive, or has no valid embedding.
            RepositoryError: On unexpected database errors.

        Complexity: O(1) — indexed lookup.
        """
        stmt = (
            select(*self._SELECT_COLUMNS)
            .select_from(User)
            .join(
                FaceEmbedding,
                and_(
                    User.id == FaceEmbedding.user_id,
                    User.is_active.is_(True),
                ),
            )
            .where(User.id == user_id)
        )

        try:
            result = await db.execute(stmt)
            row = result.one_or_none()
        except Exception as exc:
            raise RepositoryError(
                f"Failed to fetch embedding for user {user_id}"
            ) from exc

        if row is None:
            raise EmbeddingNotFound(
                f"No embedding found for user {user_id}"
            )

        self._validate_embedding(row.embedding, user_id)
        return _row_to_domain(row)

    async def embedding_exists(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> bool:
        """Check whether a given user has a face embedding enrolled.

        Args:
            db: Active async database session.
            user_id: UUID of the user to check.

        Returns:
            ``True`` if the user is active and has a non-null embedding
            of the correct dimension (512), ``False`` otherwise.

        Raises:
            RepositoryError: On unexpected database errors.

        Complexity: O(1) — indexed lookup.
        """
        stmt = (
            select(FaceEmbedding.embedding)
            .select_from(User)
            .join(
                FaceEmbedding,
                and_(
                    User.id == FaceEmbedding.user_id,
                    User.is_active.is_(True),
                ),
            )
            .where(User.id == user_id)
        )

        try:
            result = await db.execute(stmt)
            embedding = result.scalar_one_or_none()
        except Exception as exc:
            raise RepositoryError(
                f"Failed to check embedding existence for user {user_id}"
            ) from exc

        if embedding is None:
            return False

        try:
            self._validate_embedding(embedding, user_id)
        except InvalidEmbeddingRecord:
            return False

        return True

    async def count_embeddings(
        self,
        db: AsyncSession,
    ) -> int:
        """Return the number of enrolled face embeddings.

        Counts only active users who have a face embedding record.
        Note that this is an approximate count — it does **not**
        validate embedding dimensions as part of the counting
        operation.

        Args:
            db: Active async database session.

        Returns:
            The count of active users with an embedding record.

        Raises:
            RepositoryError: On unexpected database errors.

        Complexity: O(N) scan (COUNT with JOIN).
        """
        stmt = (
            select(func.count())
            .select_from(User)
            .join(
                FaceEmbedding,
                and_(
                    User.id == FaceEmbedding.user_id,
                    User.is_active.is_(True),
                ),
            )
        )

        try:
            result = await db.execute(stmt)
            return result.scalar_one() or 0
        except Exception as exc:
            raise RepositoryError(
                "Failed to count embeddings"
            ) from exc

    async def search_embeddings(
        self,
        db: AsyncSession,
        *,
        department: str | None = None,
        role: str | None = None,
        active_only: bool = True,
    ) -> Sequence[StoredEmbedding]:
        """Search enrolled embeddings by department, role, and/or status.

        All criteria are AND-ed together.  When a criterion is
        ``None`` it is omitted from the WHERE clause.

        Args:
            db: Active async database session.
            department: If provided, only embeddings for users in this
                department are returned.
            role: If provided, only embeddings for users with this
                role are returned.
            active_only: When ``True`` (default), only embeddings for
                active users are returned.

        Returns:
            A sequence of matching :class:`StoredEmbedding` instances.

        Raises:
            RepositoryError: On unexpected database errors.

        Complexity: O(N) on the number of active users.
        """
        stmt = (
            select(*self._SELECT_COLUMNS)
            .select_from(User)
            .join(FaceEmbedding)
        )

        where_clauses: list[Any] = []

        if active_only:
            where_clauses.append(User.is_active.is_(True))

        if department is not None:
            where_clauses.append(User.department == department)

        if role is not None:
            where_clauses.append(User.role == role)

        if where_clauses:
            stmt = stmt.where(and_(*where_clauses))

        return await self._fetch_embeddings(db, stmt)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _fetch_embeddings(
        self,
        db: AsyncSession,
        stmt: Any = None,
    ) -> Sequence[StoredEmbedding]:
        """Execute a query and map results to domain objects.

        Performs per-row validation and silently skips corrupt records
        (logging a warning).

        Args:
            db: Active async database session.
            stmt: SQLAlchemy select statement.  When ``None``, the
                default multi-row fetch is used (active users only).

        Returns:
            A sequence of valid :class:`StoredEmbedding` instances.

        Raises:
            RepositoryError: On unexpected database errors.
        """
        if stmt is None:
            stmt = self._default_select()

        try:
            result = await db.execute(stmt)
            rows = result.all()
        except Exception as exc:
            raise RepositoryError(
                "Failed to fetch embeddings from database"
            ) from exc

        embeddings: list[StoredEmbedding] = []
        for row in rows:
            try:
                self._validate_embedding(row.embedding, row.id)
                embeddings.append(_row_to_domain(row))
            except (InvalidEmbeddingRecord, TypeError, ValueError) as exc:
                logger.warning(
                    "Skipping corrupt embedding for user %s: %s",
                    row.id,
                    exc,
                )
                continue

        return embeddings

    def _default_select(self) -> Any:
        """Build the default multi-row select statement.

        Joins ``users`` with ``face_embeddings`` on the FK and
        restricts to active users.
        """
        return (
            select(*self._SELECT_COLUMNS)
            .select_from(User)
            .join(
                FaceEmbedding,
                and_(
                    User.id == FaceEmbedding.user_id,
                    User.is_active.is_(True),
                ),
            )
        )

    @staticmethod
    def _validate_embedding(
        embedding: object,
        user_id: uuid.UUID,
    ) -> None:
        """Validate that an embedding is non-null, has correct dims,
        and contains only finite numeric values.

        Args:
            embedding: The raw embedding value from the database.
            user_id: The owning user's UUID (used in error messages).

        Raises:
            InvalidEmbeddingRecord: When the embedding is ``None``,
                not a list, has length != 512, contains NaN or Inf,
                or cannot be converted to a float32 array.
        """
        if embedding is None:
            raise InvalidEmbeddingRecord(
                f"Embedding for user {user_id} is NULL"
            )
        if not isinstance(embedding, list):
            raise InvalidEmbeddingRecord(
                f"Embedding for user {user_id} has type "
                f"{type(embedding).__name__}, expected list"
            )
        if len(embedding) != 512:
            raise InvalidEmbeddingRecord(
                f"Embedding for user {user_id} has dimension "
                f"{len(embedding)}, expected 512"
            )

        try:
            arr = np.asarray(embedding, dtype=np.float32)
        except (ValueError, TypeError) as exc:
            raise InvalidEmbeddingRecord(
                f"Embedding for user {user_id} could not be converted "
                f"to a numeric array: {exc}"
            ) from exc

        if not np.isfinite(arr).all():
            raise InvalidEmbeddingRecord(
                f"Embedding for user {user_id} contains NaN or "
                f"infinite values"
            )


# ======================================================================
# Module-level helpers
# ======================================================================


def _row_to_domain(row: Any) -> StoredEmbedding:
    """Map a SQLAlchemy result row to a :class:`StoredEmbedding`.

    Args:
        row: A row result from a SQLAlchemy ``execute()`` call.

    Returns:
        A domain object reflecting the row data.
    """
    return StoredEmbedding(
        user_id=row.id,
        full_name=row.full_name,
        employee_id=row.employee_id,
        department=row.department,
        model_name=row.model_name,
        embedding=row.embedding,
        created_at=row.embedding_created_at,
        updated_at=row.embedding_updated_at,
    )
