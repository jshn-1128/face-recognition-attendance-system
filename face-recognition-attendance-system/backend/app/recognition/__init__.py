from app.recognition.exceptions import (
    NoEmbeddingsException,
    RecognitionException,
    RecognitionFailedException,
    RecognitionModelException,
    RecognitionThresholdException,
    UnknownPersonException,
)
from app.recognition.matcher import (
    calculate_confidence,
    cosine_similarity,
    euclidean_distance,
    find_best_match,
    normalize_vector,
)
from app.recognition.repository import (
    EmbeddingNotFound,
    InvalidEmbeddingRecord,
    RecognitionRepository,
    RepositoryError,
    StoredEmbedding,
)
from app.recognition.schemas import (
    RecognitionCandidate,
    RecognitionFailure,
    RecognitionMetadata,
    RecognitionResponse,
)
from app.recognition.service import RecognitionService

__all__ = [
    "RecognitionService",
    "RecognitionRepository",
    "StoredEmbedding",
    "EmbeddingNotFound",
    "InvalidEmbeddingRecord",
    "RepositoryError",
    "RecognitionCandidate",
    "RecognitionResponse",
    "RecognitionFailure",
    "RecognitionMetadata",
    "RecognitionException",
    "RecognitionFailedException",
    "UnknownPersonException",
    "RecognitionThresholdException",
    "RecognitionModelException",
    "NoEmbeddingsException",
    "normalize_vector",
    "cosine_similarity",
    "euclidean_distance",
    "find_best_match",
    "calculate_confidence",
]
