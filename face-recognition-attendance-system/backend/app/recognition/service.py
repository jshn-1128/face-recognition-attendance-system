"""Recognition service — orchestrates the recognition pipeline.

Coordinates the :class:`RecognitionRepository` and the matcher
(:func:`find_best_match`) without performing any database queries,
vector mathematics, or AI operations directly.  The service is a
pure orchestration layer that translates between domain objects
and delegates computation to specialised components.
"""

import logging
import uuid
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.recognition.matcher import (
    RecognitionMatch,
    calculate_confidence,
    cosine_similarity,
    find_best_match,
)
from app.recognition.repository import (
    EmbeddingNotFound,
    RecognitionRepository,
    RepositoryError,
    StoredEmbedding,
)

logger = logging.getLogger(__name__)


# ======================================================================
# Domain model
# ======================================================================


@dataclass(frozen=True)
class RecognitionResult:
    """Immutable result of a face recognition operation.

    This is the **only** object returned by the service layer.
    Consumers (routers, attendance engine, analytics, reports)
    receive this object and never interact with ``RecognitionMatch``
    or ``StoredEmbedding`` directly.

    Attributes:
        matched: Whether a match was found above the confidence
            threshold.
        user_id: UUID of the matched user (``None`` when no match).
        full_name: Full name of the matched user (``None`` when no
            match).
        employee_id: Employee identifier of the matched user
            (``None`` when no match or user has no employee ID).
        department: Department of the matched user (``None`` when
            no match or user has no department).
        similarity: Cosine similarity of the best match (``0.0``
            when no match).
        confidence: Confidence percentage derived from the similarity
            (``0.0`` when no match).
        model_name: Name of the AI model that produced the matched
            embedding (``None`` when no match).
        metadata: Extra fields from the winning candidate record.
    """

    matched: bool
    user_id: uuid.UUID | None
    full_name: str | None
    employee_id: str | None
    department: str | None
    similarity: float
    confidence: float
    model_name: str | None
    metadata: Mapping[str, Any]


@dataclass(frozen=True)
class VerificationResult:
    """Immutable result of a 1:1 face verification operation.

    Returned by :meth:`RecognitionService.verify` and consumed by the
    router layer.  Consumers receive this object and never interact
    with ``StoredEmbedding`` or raw matcher values directly.

    Attributes:
        verified: ``True`` when the query embedding matches the claimed
            user's enrolled embedding above the configured threshold.
        user_id: UUID of the claimed user.
        full_name: Full name of the claimed user (``None`` when the
            lookup succeeded but the profile has no name).
        employee_id: Employee identifier of the claimed user
            (``None`` when not set).
        department: Department of the claimed user (``None`` when
            not set).
        similarity: Cosine similarity between the query and stored
            embeddings.
        confidence: Confidence percentage derived from the similarity.
        threshold: Similarity threshold used for the verification
            decision.
        model_name: Name of the AI model that produced the stored
            embedding.
        message: Human-readable outcome message.
    """

    verified: bool
    user_id: uuid.UUID
    full_name: str | None
    employee_id: str | None
    department: str | None
    similarity: float
    confidence: float
    threshold: float
    model_name: str | None
    message: str


# Sentinal used for the no-match case to avoid repeated allocations.
_NOT_MATCHED = RecognitionResult(
    matched=False,
    user_id=None,
    full_name=None,
    employee_id=None,
    department=None,
    similarity=0.0,
    confidence=0.0,
    model_name=None,
    metadata={},
)


# ======================================================================
# Service-level exceptions
#
# These are deliberately **not** HTTP exceptions — the service layer
# is below the router layer and must not depend on FastAPI.
# ======================================================================


class RecognitionServiceError(Exception):
    """Base exception for service-level errors.

    Raised when the recognition pipeline encounters an unexpected
    failure (database errors, corrupt data, invalid input).
    """


# ======================================================================
# Service
# ======================================================================


class RecognitionService:
    """Orchestrates face recognition workflows.

    The service is the bridge between the :class:`RecognitionRepository`
    (database access) and the matcher (similarity search).  It does
    **not** perform any SQL, NumPy, image processing, or AI operations
    itself — it delegates everything to the injected dependencies.

    The service is **stateless** and safe for concurrent use with
    separate database sessions.
    """

    def __init__(
        self,
        repository: RecognitionRepository | None = None,
    ) -> None:
        self._repository = repository or RecognitionRepository()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def recognize(
        self,
        db: AsyncSession,
        query_embedding: Sequence[float],
    ) -> RecognitionResult:
        """Recognise a face embedding against all enrolled embeddings.

        Workflow:

        1.  Validate the query embedding (non-null, non-empty, sequence).
        2.  Load all enrolled embeddings from the repository.
        3.  If the database is empty return ``matched=False``
            (this is **not** an exception).
        4.  Convert ``StoredEmbedding`` objects into matcher-compatible
            candidate dicts.
        5.  Call :func:`find_best_match` exactly once.
        6.  Translate the low-level ``RecognitionMatch`` into a
            ``RecognitionResult``.

        Args:
            db: Active async database session.
            query_embedding: A face embedding vector (typically
                512-dimensional).

        Returns:
            A :class:`RecognitionResult` describing the match outcome.
            When no enrolled embeddings exist or no candidate meets
            the similarity threshold, ``matched`` is ``False`` and all
            identity fields are ``None``.

        Raises:
            RecognitionServiceError: If the query embedding is invalid
                (``None``, wrong type, empty), a database error occurs,
                or the matcher encounters a corrupt candidate.

        Complexity: O(N × D) — N enrolled embeddings, D embedding
            dimensions.

        Thread safety: Fully stateless — safe for concurrent use.
        """
        self._validate_query(query_embedding)

        try:
            embeddings = await self._repository.get_all_embeddings(db)
        except RepositoryError as exc:
            logger.error("Failed to load enrolled embeddings: %s", exc)
            raise RecognitionServiceError(
                "Failed to load enrolled embeddings from database"
            ) from exc

        if not embeddings:
            logger.info("No enrolled embeddings found — returning no match")
            return _NOT_MATCHED

        candidates = self._build_candidates(embeddings)

        try:
            match: RecognitionMatch = find_best_match(
                query_embedding, candidates
            )
        except (TypeError, ValueError) as exc:
            logger.error("Matcher error: %s", exc)
            raise RecognitionServiceError(
                f"Face recognition failed: {exc}"
            ) from exc

        return self._match_to_result(match)

    async def count_registered_faces(
        self,
        db: AsyncSession,
    ) -> int:
        """Return the number of enrolled face embeddings.

        Delegates to :meth:`RecognitionRepository.count_embeddings`.

        Args:
            db: Active async database session.

        Returns:
            The count of enrolled embeddings.

        Raises:
            RecognitionServiceError: On database error.

        Complexity: O(N) — delegated to the repository.
        """
        try:
            return await self._repository.count_embeddings(db)
        except RepositoryError as exc:
            raise RecognitionServiceError(
                "Failed to count registered faces"
            ) from exc

    async def has_registered_face(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> bool:
        """Check whether a specific user has a registered face embedding.

        Delegates to :meth:`RecognitionRepository.embedding_exists`.

        Args:
            db: Active async database session.
            user_id: UUID of the user to check.

        Returns:
            ``True`` if the user is active and has a valid embedding.

        Raises:
            RecognitionServiceError: On database error.

        Complexity: O(1) — indexed lookup.
        """
        try:
            return await self._repository.embedding_exists(db, user_id)
        except RepositoryError as exc:
            raise RecognitionServiceError(
                f"Failed to check embedding for user {user_id}"
            ) from exc

    async def verify(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        query_embedding: Sequence[float],
        threshold: float = 0.65,
    ) -> VerificationResult:
        """Verify a face embedding against a claimed user's enrolled embedding.

        1:1 verification answers "is this the claimed user?" —
        it compares the query embedding against *one* stored embedding
        rather than searching all enrolled users.

        Workflow:

        1.  Validate the query embedding (non-null, non-empty, sequence).
        2.  Fetch the claimed user's stored embedding (O(1) lookup).
        3.  Compute cosine similarity between query and stored embedding.
        4.  Derive a confidence percentage from the similarity.
        5.  Compare against the configured threshold.
        6.  Build and return a ``VerificationResult``.

        Args:
            db: Active async database session.
            user_id: UUID of the claimed user to verify against.
            query_embedding: A face embedding vector (typically
                512-dimensional).
            threshold: Minimum cosine similarity required for a
                positive verification.  Defaults to ``0.65``.

        Returns:
            A :class:`VerificationResult` describing the verification
            outcome.  When the similarity is below *threshold*,
            ``verified`` is ``False``.

        Raises:
            EmbeddingNotFound: If the claimed user does not exist,
                is inactive, or has no enrolled embedding.
            RecognitionServiceError: If the query embedding is invalid
                (``None``, wrong type, empty), a database error occurs,
                or the matcher encounters a corrupt stored embedding.

        Complexity: O(D) — D embedding dimensions.
            Single lookup, single pairwise similarity computation.

        Thread safety: Fully stateless — safe for concurrent use.
        """
        self._validate_query(query_embedding)

        try:
            stored = await self._repository.get_embedding_by_user_id(
                db, user_id
            )
        except RepositoryError as exc:
            logger.error(
                "Failed to fetch embedding for user %s: %s", user_id, exc
            )
            raise RecognitionServiceError(
                f"Failed to fetch enrolled embedding for user {user_id}"
            ) from exc

        try:
            similarity = cosine_similarity(query_embedding, stored.embedding)
            confidence = calculate_confidence(similarity)
        except (TypeError, ValueError) as exc:
            logger.error(
                "Similarity computation failed for user %s: %s",
                user_id,
                exc,
            )
            raise RecognitionServiceError(
                f"Face verification failed: {exc}"
            ) from exc

        verified = similarity >= threshold

        return VerificationResult(
            verified=verified,
            user_id=stored.user_id,
            full_name=stored.full_name,
            employee_id=stored.employee_id,
            department=stored.department,
            similarity=similarity,
            confidence=confidence,
            threshold=threshold,
            model_name=stored.model_name,
            message=(
                "Identity verified."
                if verified
                else "Identity could not be verified."
            ),
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_query(query_embedding: object) -> None:
        """Validate the query embedding before processing.

        Args:
            query_embedding: The raw query embedding value.

        Raises:
            RecognitionServiceError: If the embedding is ``None``,
                a :class:`str`/:class:`bytes`, not a :class:`Sequence`,
                or empty.
        """
        if query_embedding is None:
            raise RecognitionServiceError(
                "Query embedding must not be None"
            )
        if isinstance(query_embedding, (str, bytes)):
            raise RecognitionServiceError(
                f"Query embedding must be a sequence of numbers, "
                f"got {type(query_embedding).__name__}"
            )
        if not isinstance(query_embedding, Sequence):
            raise RecognitionServiceError(
                f"Query embedding must be a sequence, "
                f"got {type(query_embedding).__name__}"
            )
        if len(query_embedding) == 0:
            raise RecognitionServiceError(
                "Query embedding must not be empty"
            )

    @staticmethod
    def _build_candidates(
        embeddings: Sequence[StoredEmbedding],
    ) -> list[dict[str, Any]]:
        """Convert ``StoredEmbedding`` objects into matcher candidates.

        The matcher expects a sequence of dicts with at minimum
        ``candidate_id`` and ``embedding`` keys.  Any additional keys
        are preserved verbatim as metadata by the matcher and will
        be available in ``RecognitionMatch.metadata``.

        Args:
            embeddings: Sequence of enrolled embeddings from the
                repository.

        Returns:
            A list of candidate dicts ready for :func:`find_best_match`.
        """
        return [
            {
                "candidate_id": emb.user_id,
                "embedding": emb.embedding,
                "full_name": emb.full_name,
                "employee_id": emb.employee_id,
                "department": emb.department,
                "model_name": emb.model_name,
            }
            for emb in embeddings
        ]

    @staticmethod
    def _match_to_result(match: RecognitionMatch) -> RecognitionResult:
        """Convert a matcher ``RecognitionMatch`` to a service result.

        When the match is positive, identity fields are extracted from
        ``match.metadata`` (which the matcher preserved from the
        candidate dicts).  This avoids a second lookup through the
        original candidate list.

        Args:
            match: The result from :func:`find_best_match`.

        Returns:
            A fully populated :class:`RecognitionResult`.
        """
        if not match.matched:
            return _NOT_MATCHED

        meta = match.metadata or {}

        return RecognitionResult(
            matched=True,
            user_id=match.candidate_id,
            full_name=meta.get("full_name"),
            employee_id=meta.get("employee_id"),
            department=meta.get("department"),
            similarity=match.similarity,
            confidence=match.confidence,
            model_name=meta.get("model_name"),
            metadata=meta,
        )
