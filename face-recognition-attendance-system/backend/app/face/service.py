import io
import logging
import uuid
from pathlib import Path

from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession

from app.face.detector import initialize as init_detector, read_image_from_bytes
from app.face.embedding import generate_embedding
from app.face.exceptions import (
    EmbeddingAlreadyExistsException,
    EmbeddingNotFoundException,
    InvalidImageException,
    UnsupportedImageException,
)
from app.face.models import FaceEmbedding
from app.face.repository import (
    create_embedding as create_embedding_repo,
    delete_embedding as delete_embedding_repo,
    embedding_exists,
    get_embedding_by_user,
    update_embedding as update_embedding_repo,
)
from app.face.schemas import FaceRegisterResponse, FaceResponse
from app.core.config import settings

logger = logging.getLogger(__name__)

_ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}
_ALLOWED_EXTENSIONS = {f".{ext}" for ext in settings.SUPPORTED_IMAGE_TYPES_LIST}
_MAX_SIZE_BYTES = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024


def _validate_image(filename: str, content_type: str | None, file_size: int) -> None:
    """Validate image file metadata before processing."""
    if file_size == 0:
        raise InvalidImageException("Uploaded file is empty")
    if file_size > _MAX_SIZE_BYTES:
        raise InvalidImageException(
            f"Image size exceeds maximum allowed size of {settings.MAX_IMAGE_SIZE_MB} MB"
        )
    ext = Path(filename).suffix.lower()
    if ext not in _ALLOWED_EXTENSIONS:
        raise UnsupportedImageException()
    if content_type and content_type not in _ALLOWED_MIME_TYPES:
        raise UnsupportedImageException()


def _validate_image_content(image_bytes: bytes) -> None:
    """Validate that the bytes represent a readable image."""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()
    except Exception as exc:
        raise InvalidImageException("Image file is corrupted or unreadable") from exc


def _get_storage_path() -> Path:
    """Return the absolute storage directory path, creating it if needed."""
    storage = Path(settings.FACE_STORAGE_PATH)
    if not storage.is_absolute():
        storage = Path.cwd() / storage
    storage.mkdir(parents=True, exist_ok=True)
    return storage


def _save_image(image_bytes: bytes, filename: str) -> str:
    """Save image to disk with a UUID filename, returning the relative path."""
    storage = _get_storage_path()
    ext = Path(filename).suffix.lower()
    unique_name = f"{uuid.uuid4()}{ext}"
    relative_path = f"{settings.FACE_STORAGE_PATH}/{unique_name}"
    absolute_path = storage / unique_name
    absolute_path.write_bytes(image_bytes)
    logger.info("Image saved: %s", relative_path)
    return relative_path


def _delete_image(image_path: str) -> None:
    """Delete an image file from disk given its relative path."""
    path = Path(image_path)
    if not path.is_absolute():
        path = Path.cwd() / path
    if path.exists():
        path.unlink()
        logger.info("Image deleted: %s", image_path)


async def register_face(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    filename: str,
    content_type: str | None,
    file_size: int,
    image_bytes: bytes,
) -> FaceRegisterResponse:
    """Register a face embedding for a user.

    Workflow: validate image -> detect face -> generate embedding -> save.
    Rolls back on any failure.
    """
    _validate_image(filename, content_type, file_size)
    _validate_image_content(image_bytes)
    if await embedding_exists(db, user_id):
        raise EmbeddingAlreadyExistsException()

    init_detector(settings.FACE_MODEL_NAME)
    image = read_image_from_bytes(image_bytes)
    embedding = generate_embedding(image)
    image_path = _save_image(image_bytes, filename)

    try:
        record = await create_embedding_repo(
            db,
            user_id=user_id,
            embedding=embedding,
            model_name=settings.FACE_MODEL_NAME,
            image_path=image_path,
        )
    except Exception:
        _delete_image(image_path)
        raise

    logger.info("Face registered for user %s", user_id)
    return FaceRegisterResponse.model_validate(record)


async def get_face(db: AsyncSession, user_id: uuid.UUID) -> FaceResponse:
    """Retrieve face embedding metadata for the current user."""
    record = await get_embedding_by_user(db, user_id)
    if not record:
        raise EmbeddingNotFoundException()
    return FaceResponse.model_validate(record)


async def update_face(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    filename: str,
    content_type: str | None,
    file_size: int,
    image_bytes: bytes,
) -> FaceResponse:
    """Replace the existing face embedding with a new one."""
    _validate_image(filename, content_type, file_size)
    _validate_image_content(image_bytes)

    record = await get_embedding_by_user(db, user_id)
    if not record:
        raise EmbeddingNotFoundException()

    init_detector(settings.FACE_MODEL_NAME)
    image = read_image_from_bytes(image_bytes)
    embedding = generate_embedding(image)
    new_image_path = _save_image(image_bytes, filename)

    old_image_path = record.image_path

    try:
        updated = await update_embedding_repo(
            db,
            record,
            embedding=embedding,
            image_path=new_image_path,
            model_name=settings.FACE_MODEL_NAME,
        )
    except Exception:
        _delete_image(new_image_path)
        raise

    _delete_image(old_image_path)

    logger.info("Face embedding updated for user %s", user_id)
    return FaceResponse.model_validate(updated)


async def delete_face(db: AsyncSession, user_id: uuid.UUID) -> None:
    """Delete face embedding record and stored image."""
    record = await get_embedding_by_user(db, user_id)
    if not record:
        raise EmbeddingNotFoundException()

    image_path = record.image_path
    await delete_embedding_repo(db, record)
    _delete_image(image_path)

    logger.info("Face embedding deleted for user %s", user_id)
