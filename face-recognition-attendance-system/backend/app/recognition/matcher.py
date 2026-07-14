"""Mathematical functions for face-vector comparison.

This module contains the core similarity and distance algorithms
used during face recognition.  No AI models are loaded here — only
pure mathematical operations on embedding vectors.

The module is a **pure library** with zero dependencies beyond NumPy.
It knows nothing about FastAPI, databases, filesystems, or the rest
of the application.  It can be imported into any Python consumer
(FastAPI, CLI, desktop app, batch processor, mobile backend)
without modification.
"""

import numpy as np
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _validate_vector(v: Sequence[float], name: str = "vector") -> np.ndarray:
    """Validate a vector and convert to a 1-D float64 NumPy array.

    ``float64`` preserves the precision of Python ``float`` inputs
    and avoids the precision loss that ``float32`` would introduce
    during normalisation.  :func:`normalize_vector` converts the
    result to ``float32`` after computing the norm.

    Args:
        v: Input vector to validate.
        name: Name of the vector used in error messages.

    Returns:
        1-D ``float64`` NumPy array.

    Raises:
        TypeError: If *v* is ``None`` or is not a sequence.
        ValueError: If *v* is empty, not 1-D, contains NaN or
            infinite values, or has a non-numeric dtype.

    Time complexity: O(n)
    Space complexity: O(n)
    """
    if v is None:
        raise TypeError(f"{name} must not be None")
    arr = np.asarray(v, dtype=np.float64)
    if arr.ndim != 1:
        raise ValueError(
            f"{name} must be 1-dimensional, got {arr.ndim}"
        )
    if arr.shape[0] == 0:
        raise ValueError(f"{name} must not be empty")
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} contains NaN or infinite values")
    return arr


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def normalize_vector(v: Sequence[float]) -> np.ndarray:
    """L2-normalise a vector to unit Euclidean length.

    The input is validated in ``float64``, normalised in ``float64``,
    and the result is returned as a ``float32`` NumPy array.
    The output satisfies ``||v̂|| ≈ 1`` (within float32 precision).

    Args:
        v: Input vector.

    Returns:
        L2-normalised vector as a 1-D ``float32`` NumPy array.

    Raises:
        TypeError: If *v* is ``None`` or is not a sequence.
        ValueError: If *v* is empty, contains NaN/Inf, is a
            zero vector, or has non-numeric dtype.

    Time complexity: O(n)
    Space complexity: O(n)

    Examples:
        >>> normalize_vector([3.0, 4.0])
        array([0.6, 0.8], dtype=float32)
    """
    arr = _validate_vector(v)
    norm = float(np.linalg.norm(arr))
    if norm == 0.0:
        raise ValueError("cannot normalise a zero vector")
    result = (arr / norm).astype(np.float32)
    return result


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    """Compute the cosine similarity between two vectors.

    Both vectors are **L2-normalised internally** before the dot
    product is taken.  All arithmetic is performed in ``float64``
    to preserve precision.  The result is clamped to ``[-1.0, 1.0]``
    to eliminate floating-point precision artefacts.

    Args:
        a: First vector.
        b: Second vector.

    Returns:
        Cosine similarity as a Python ``float`` in ``[-1.0, 1.0]``.

    Raises:
        TypeError: If either input is ``None`` or not a sequence.
        ValueError: If either input is empty, contains NaN/Inf,
            is a zero vector, or dimensions differ.

    Time complexity: O(n)
    Space complexity: O(n)

    Examples:
        >>> cosine_similarity([1.0, 2.0, 3.0], [1.0, 2.0, 3.0])
        1.0
        >>> cosine_similarity([1.0, 0.0], [0.0, 1.0])
        0.0
        >>> cosine_similarity([1.0, 0.0], [-1.0, 0.0])
        -1.0
    """
    arr_a = _validate_vector(a, "vector_a")
    arr_b = _validate_vector(b, "vector_b")
    if arr_a.shape[0] != arr_b.shape[0]:
        raise ValueError(
            f"dimension mismatch: vector_a has {arr_a.shape[0]} dimensions, "
            f"vector_b has {arr_b.shape[0]} dimensions"
        )
    norm_a = float(np.linalg.norm(arr_a))
    norm_b = float(np.linalg.norm(arr_b))
    if norm_a == 0.0 or norm_b == 0.0:
        raise ValueError(
            "cannot compute cosine similarity with a zero vector"
        )
    dot = float(np.dot(arr_a / norm_a, arr_b / norm_b))
    return float(np.clip(dot, -1.0, 1.0))


def euclidean_distance(a: Sequence[float], b: Sequence[float]) -> float:
    """Compute the Euclidean distance between two vectors.

    .. note::

        **Design choice — no internal L2 normalisation.**
        Euclidean distance preserves magnitude information that is
        lost when vectors are normalised.  In face recognition the
        magnitude of an embedding can carry signal about image quality
        or prediction confidence.  Consumers who need a magnitude-
        invariant metric should use :func:`cosine_similarity` instead.

        When both inputs *are* unit vectors (e.g. from InsightFace
        ``buffalo_l``) the relationship is:
        ``d(a, b) = sqrt(2 - 2 * cos(a, b))``

    Args:
        a: First vector.
        b: Second vector.

    Returns:
        Non-negative Euclidean distance as a Python ``float``.

    Raises:
        TypeError: If either input is ``None`` or not a sequence.
        ValueError: If either input is empty, contains NaN/Inf,
            has non-numeric dtype, or dimensions differ.

    Time complexity: O(n)
    Space complexity: O(n)

    Examples:
        >>> euclidean_distance([0.0, 0.0], [3.0, 4.0])
        5.0
    """
    arr_a = _validate_vector(a, "vector_a")
    arr_b = _validate_vector(b, "vector_b")
    if arr_a.shape[0] != arr_b.shape[0]:
        raise ValueError(
            f"dimension mismatch: vector_a has {arr_a.shape[0]} dimensions, "
            f"vector_b has {arr_b.shape[0]} dimensions"
        )
    diff = arr_a - arr_b
    squared = float(np.dot(diff, diff))
    return float(np.sqrt(max(squared, 0.0)))


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class RecognitionMatch:
    """Result of a face-recognition ``find_best_match`` operation.

    Attributes:
        matched: ``True`` when the best similarity ≥ *threshold*.
        candidate_id: Identifier of the best-matching candidate
            (``None`` when *matched* is ``False``).
        similarity: Cosine similarity of the best match
            (``0.0`` when nobody matched).
        confidence: Confidence percentage derived from the similarity
            (``0.0`` when nobody matched).
        metadata: Extra fields from the winning candidate record
            (``None`` when nobody matched or candidate had no extras).
    """

    matched: bool = False
    candidate_id: Any = None
    similarity: float = 0.0
    confidence: float = 0.0
    metadata: dict | None = None


# ---------------------------------------------------------------------------
# Score → confidence
# ---------------------------------------------------------------------------


def calculate_confidence(similarity: float) -> float:
    """Convert a cosine-similarity score into a confidence percentage.

    The formula is ``confidence = max(0.0, clamp(s, -1, 1) × 100)``:

    ==================  ===========
    Similarity           Confidence
    ==================  ===========
    1.0                 100.0
    0.95                 95.0
    0.73                 73.0
    0.0                   0.0
    -0.5                  0.0
    ==================  ===========

    Args:
        similarity: Raw cosine similarity (ideally in ``[-1.0, 1.0]``).

    Returns:
        Confidence percentage as a Python ``float`` in ``[0.0, 100.0]``.

    Time complexity: O(1)
    Space complexity: O(1)

    Examples:
        >>> calculate_confidence(1.0)
        100.0
        >>> calculate_confidence(0.95)
        95.0
        >>> calculate_confidence(0.73)
        73.0
        >>> calculate_confidence(-0.5)
        0.0
    """
    clamped = max(-1.0, min(similarity, 1.0))
    return float(max(0.0, clamped * 100.0))


# ---------------------------------------------------------------------------
# Candidate extraction
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _PreparedCandidates:
    """Pre-processed candidate data ready for similarity search.

    Attributes:
        embedding_matrix: ``(n, d)`` float32 array where every row is an
            L2-normalised candidate embedding.
        candidate_ids: Parallel list of candidate identifiers.
        metadata_list: Parallel list of extra-field dicts (may be empty).
    """

    embedding_matrix: np.ndarray
    candidate_ids: list[Any]
    metadata_list: list[dict]


def _prepare_candidate_matrix(
    candidates: Sequence[dict],
    dim: int,
) -> _PreparedCandidates:
    """Extract, validate, and L2-normalise every candidate embedding.

    Each candidate dict **must** contain ``candidate_id`` and
    ``embedding`` keys.  Embeddings are validated (NaN, Inf, zero-norm,
    dimension mismatch) and L2-normalised before being stored into a
    pre-allocated ``(n, d)`` float32 matrix.  Any extra keys in the
    candidate dict are preserved as metadata but are **not** validated.

    Args:
        candidates: A non-empty sequence of candidate dicts.
        dim: Expected embedding dimension (derived from the query).

    Returns:
        A :class:`_PreparedCandidates` holding the normalised matrix,
        candidate identifiers, and metadata.

    Raises:
        TypeError: If any candidate is not a dict.
        ValueError: If any candidate is missing required keys, has an
            invalid embedding, a dimension mismatch, or a zero-norm
            embedding.

    Time complexity: O(n × d)
    Space complexity: O(n × d)
    """
    n = len(candidates)
    emb_matrix = np.empty((n, dim), dtype=np.float32)
    ids: list[Any] = []
    metadata_list: list[dict] = []

    for i, candidate in enumerate(candidates):
        if not isinstance(candidate, dict):
            raise TypeError(
                f"candidate at index {i} must be a dict, "
                f"got {type(candidate).__name__}"
            )
        if "candidate_id" not in candidate:
            raise ValueError(
                f"candidate at index {i} is missing required key "
                "'candidate_id'"
            )
        if "embedding" not in candidate:
            raise ValueError(
                f"candidate at index {i} is missing required key "
                "'embedding'"
            )

        emb = _validate_vector(
            candidate["embedding"], f"candidate[{i}].embedding"
        )
        if emb.shape[0] != dim:
            raise ValueError(
                f"candidate[{i}] embedding has {emb.shape[0]} "
                f"dimensions, expected {dim}"
            )

        norm = float(np.linalg.norm(emb))
        if norm == 0.0:
            raise ValueError(
                f"candidate[{i}] embedding is a zero vector"
            )
        emb_matrix[i] = (emb / norm).astype(np.float32)

        ids.append(candidate["candidate_id"])
        metadata_list.append(
            {
                k: v
                for k, v in candidate.items()
                if k not in ("candidate_id", "embedding")
            }
        )

    return _PreparedCandidates(
        embedding_matrix=emb_matrix,
        candidate_ids=ids,
        metadata_list=metadata_list,
    )


# ---------------------------------------------------------------------------
# Best-match search
# ---------------------------------------------------------------------------


def find_best_match(
    query_vector: Sequence[float],
    candidates: Sequence[dict],
    threshold: float = 0.65,
) -> RecognitionMatch:
    """Find the closest matching candidate from a list of candidates.

    The algorithm:

    1.  L2-normalise the query vector once.
    2.  Delegate candidate extraction, validation, and normalisation to
        :func:`_prepare_candidate_matrix`.
    3.  Compute all cosine similarities with a single vectorised dot
        product ``similarities = E @ q_norm``.
    4.  Locate the best index via ``np.argmax`` (deterministic
        tie-breaking — the first max wins).
    5.  If the best similarity is below *threshold*, return
        ``matched=False`` — an unknown person is **not** an error.

    Args:
        query_vector: The query face embedding.
        candidates: A sequence of candidate dicts.  Each dict **must**
            contain at least ``candidate_id`` (any hashable identifier)
            and ``embedding`` (``Sequence[float]``).  Any additional
            keys are preserved verbatim in ``RecognitionMatch.metadata``.
        threshold: Minimum cosine similarity required for a positive
            match.  Default ``0.65``.

    Returns:
        A :class:`RecognitionMatch` describing the result.

    Raises:
        TypeError: If the query vector is ``None``, or if a candidate
            is not a dict.
        ValueError: If the query vector is empty, contains NaN/Inf,
            is a zero vector, or has non-numeric dtype.  Also if a
            candidate is missing required keys, has an invalid
            embedding, or has a dimension different from the query.

    Time complexity: O(n × d) — n candidates, d embedding dimensions.
    Space complexity: O(n × d) for the embedding matrix.

    Examples:
        >>> candidates = [
        ...     {"candidate_id": "alice", "embedding": [0.1, 0.2, 0.3]},
        ...     {"candidate_id": "bob",   "embedding": [0.9, 0.8, 0.7]},
        ...     {"candidate_id": "carol", "embedding": [0.4, 0.5, 0.6]},
        ... ]
        >>> result = find_best_match([0.85, 0.75, 0.65], candidates)
        >>> result.matched
        True
        >>> result.candidate_id
        'bob'
    """
    # ------------------------------------------------------------------
    # 1.  Validate & normalise the query vector once.
    #     normalize_vector raises TypeError/ValueError as appropriate.
    # ------------------------------------------------------------------
    q_norm = normalize_vector(query_vector)
    dim: int = int(q_norm.shape[0])

    # ------------------------------------------------------------------
    # 2.  Empty candidate list → no match
    # ------------------------------------------------------------------
    if not candidates:
        return RecognitionMatch(matched=False)

    # ------------------------------------------------------------------
    # 3.  Delegate candidate extraction, validation, normalisation.
    # ------------------------------------------------------------------
    prepared = _prepare_candidate_matrix(candidates, dim)

    # ------------------------------------------------------------------
    # 4.  Vectorised similarity: E @ q_norm
    #     prepared.embedding_matrix : (n, d) float32 — unit-length rows
    #     q_norm                    : (d,)   float32 — unit-length
    #     similarities              : (n,)   float32
    # ------------------------------------------------------------------
    similarities = np.clip(
        np.dot(prepared.embedding_matrix, q_norm), -1.0, 1.0
    )

    # ------------------------------------------------------------------
    # 5.  Locate the best match.
    # ------------------------------------------------------------------
    best_idx = int(np.argmax(similarities))
    best_similarity = float(similarities[best_idx])
    best_confidence = calculate_confidence(best_similarity)

    # ------------------------------------------------------------------
    # 6.  Apply threshold — unknown person is NOT an error.
    # ------------------------------------------------------------------
    if best_similarity < threshold:
        return RecognitionMatch(matched=False)

    return RecognitionMatch(
        matched=True,
        candidate_id=prepared.candidate_ids[best_idx],
        similarity=best_similarity,
        confidence=best_confidence,
        metadata=prepared.metadata_list[best_idx] or None,
    )
