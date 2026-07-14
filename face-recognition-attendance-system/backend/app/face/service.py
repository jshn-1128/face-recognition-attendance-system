import asyncio
import io
import logging
import os
import uuid
from pathlib import Path

from PIL import Image
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import _add_commit_hook, _add_rollback_hook
from app.face.detector import initialize as init_detector, read_image_from_bytes
from app.face.embedding import generate_embedding
from app.face.exceptions import (
    EmbeddingAlreadyExistsException,
    EmbeddingNotFoundException,
    InvalidImageException,
    UnsupportedImageException,
)
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
    if file_size > _MAX_SIZE_BYTES:
        raise InvalidImageException(
            f"Image size exceeds maximum allowed size of {settings.MAX_IMAGE_SIZE_MB} MB"
        )
    ext = Path(filename).suffix.lower()
    if ext not in _ALLOWED_EXTENSIONS:
        raise UnsupportedImageException()
    if content_type and content_type not in _ALLOWED_MIME_TYPES:
        raise UnsupportedImageException()


async def _validate_image_content(image_bytes: bytes) -> None:
    """Validate that the bytes represent a readable image (offloaded to thread)."""
    try:
        img = await asyncio.to_thread(Image.open, io.BytesIO(image_bytes))
        await asyncio.to_thread(img.verify)
    except Exception as exc:
        raise InvalidImageException("Image file is corrupted or unreadable") from exc


def _get_storage_path() -> Path:
    """Return the absolute storage directory path, creating it if needed."""
    storage = Path(settings.FACE_STORAGE_PATH)
    if not storage.is_absolute():
        storage = Path.cwd() / storage
    storage.mkdir(parents=True, exist_ok=True)
    return storage


def _temp_path(unique_name: str) -> str:
    """Return a temporary relative path for an image being processed."""
    return f"{settings.FACE_STORAGE_PATH}/tmp_{unique_name}"


def _final_path(unique_name: str) -> str:
    """Return the final relative path for an image after successful commit."""
    return f"{settings.FACE_STORAGE_PATH}/{unique_name}"


def _uuid_filename(filename: str) -> str:
    """Generate a unique filename with the original extension."""
    ext = Path(filename).suffix.lower()
    return f"{uuid.uuid4()}{ext}"


async def _save_image_to_temp(image_bytes: bytes, unique_name: str) -> str:
    """Save image bytes to a temporary path and return the relative path.

    The image is saved to a temp location first.  It will be renamed to the
    final location only after the database commit succeeds.
    """
    storage = _get_storage_path()
    temp_rel = _temp_path(unique_name)
    temp_abs = storage / f"tmp_{unique_name}"
    await asyncio.to_thread(temp_abs.write_bytes, image_bytes)
    logger.debug("Temp image saved: %s", temp_rel)
    return temp_rel


async def _delete_image(image_path: str) -> None:
    """Delete an image file from disk given its relative path (offloaded to thread)."""
    path = Path(image_path)
    if not path.is_absolute():
        path = Path.cwd() / path
    if path.exists():
        await asyncio.to_thread(path.unlink)
        logger.info("Image deleted: %s", image_path)


async def extract_embedding(
    *,
    filename: str,
    content_type: str | None,
    file_size: int,
    image_bytes: bytes,
) -> list[float]:
    """Extract a face embedding from raw image bytes.

    Workflow:
        1. Validate image metadata (MIME, extension, size).
        2. Validate image content (decodable, not corrupt).
        3. Initialise the face detector (idempotent — no-op if already loaded).
        4. Decode the image, detect exactly one face, generate a 512-d embedding.

    This is the **single** entry point that every consumer (registration,
    recognition, future attendance) should use to obtain an embedding from
    an uploaded image.  It performs **no** database operations and **no**
    file I/O beyond reading the provided bytes.

    Args:
        filename: Original filename (used to infer extension for validation).
        content_type: MIME type from the upload (may be ``None``).
        file_size: Size of the image in bytes.
        image_bytes: Raw image file bytes.

    Returns:
        A 512-dimensional face embedding as ``list[float]``.

    Raises:
        InvalidImageException: Image is corrupted or unreadable.
        UnsupportedImageException: Unsupported MIME type or file extension.
        FaceNotFoundException: No face detected in the image.
        MultipleFacesDetectedException: More than one face detected.
        FaceModelException: Face model failed to initialise.

    Thread safety: Fully stateless — safe for concurrent use.
    """
    _validate_image(filename, content_type, file_size)
    await _validate_image_content(image_bytes)
    init_detector(settings.FACE_MODEL_NAME)
    image = await read_image_from_bytes(image_bytes)
    return await generate_embedding(image)


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

    Workflow:
        1. Validate image metadata and content.
        2. Check for existing embedding (best-effort, race handled by IntegrityError catch).
        3. Detect face and generate embedding.
        4. Save image to a *temporary* path.
        5. Insert DB record with the *final* image path.
        6. On successful commit → rename temp → final.
        7. On rollback → delete temp file.
    """
    _validate_image(filename, content_type, file_size)
    await _validate_image_content(image_bytes)
    if await embedding_exists(db, user_id):
        raise EmbeddingAlreadyExistsException()

    init_detector(settings.FACE_MODEL_NAME)
    image = await read_image_from_bytes(image_bytes)
    embedding = await generate_embedding(image)

    unique_name = _uuid_filename(filename)
    final_path = _final_path(unique_name)
    temp_path = await _save_image_to_temp(image_bytes, unique_name)

    try:
        record = await create_embedding_repo(
            db,
            user_id=user_id,
            embedding=embedding,
            model_name=settings.FACE_MODEL_NAME,
            image_path=final_path,
        )
    except IntegrityError:
        await _delete_image(temp_path)
        logger.warning("Concurrent registration detected for user %s", user_id)
        raise EmbeddingAlreadyExistsException()
    except Exception:
        await _delete_image(temp_path)
        raise

    storage = _get_storage_path()
    final_abs = storage / unique_name
    temp_abs = storage / f"tmp_{unique_name}"

    def _commit_rename():
        os.rename(temp_abs, final_abs)
        logger.info("Image committed: %s", final_path)

    def _rollback_cleanup():
        if temp_abs.exists():
            temp_abs.unlink()
            logger.info("Temp image cleaned up after rollback: %s", temp_path)

    _add_commit_hook(db, _commit_rename)
    _add_rollback_hook(db, _rollback_cleanup)

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
    """Replace the existing face embedding with a new one.

    Workflow:
        1. Validate image metadata and content.
        2. Fetch existing embedding record.
        3. Detect face and generate new embedding.
        4. Save new image to a *temporary* path.
        5. Update DB record with the *final* new image path.
        6. On successful commit → rename temp → final, delete old image.
        7. On rollback → delete temp file (old image remains untouched).
    """
    _validate_image(filename, content_type, file_size)
    await _validate_image_content(image_bytes)

    record = await get_embedding_by_user(db, user_id)
    if not record:
        raise EmbeddingNotFoundException()

    init_detector(settings.FACE_MODEL_NAME)
    image = await read_image_from_bytes(image_bytes)
    embedding = await generate_embedding(image)

    unique_name = _uuid_filename(filename)
    new_final_path = _final_path(unique_name)
    new_temp_path = await _save_image_to_temp(image_bytes, unique_name)
    old_image_path = record.image_path

    try:
        updated = await update_embedding_repo(
            db,
            record,
            embedding=embedding,
            image_path=new_final_path,
            model_name=settings.FACE_MODEL_NAME,
        )
    except Exception:
        await _delete_image(new_temp_path)
        raise

    storage = _get_storage_path()
    final_abs = storage / unique_name
    temp_abs = storage / f"tmp_{unique_name}"

    def _commit_actions():
        os.rename(temp_abs, final_abs)
        logger.info("New image committed: %s", new_final_path)
        _old = Path(old_image_path)
        if not _old.is_absolute():
            _old = Path.cwd() / _old
        if _old.exists():
            _old.unlink()
            logger.info("Old image deleted after successful update: %s", old_image_path)

    def _rollback_actions():
        if temp_abs.exists():
            temp_abs.unlink()
            logger.info("Temp image cleaned up after rollback: %s", new_temp_path)

    _add_commit_hook(db, _commit_actions)
    _add_rollback_hook(db, _rollback_actions)

    logger.info("Face embedding updated for user %s", user_id)
    return FaceResponse.model_validate(updated)


async def delete_face(db: AsyncSession, user_id: uuid.UUID) -> None:
    """Delete face embedding record and stored image.

    Workflow:
        1. Fetch existing embedding record.
        2. Delete DB record.
        3. On successful commit → delete the image file.
        4. On rollback → nothing (DB record is restored, image still on disk).
    """
    record = await get_embedding_by_user(db, user_id)
    if not record:
        raise EmbeddingNotFoundException()

    image_path = record.image_path
    await delete_embedding_repo(db, record)

    path = Path(image_path)
    if not path.is_absolute():
        path = Path.cwd() / path

    def _commit_delete():
        if path.exists():
            path.unlink()
            logger.info("Image deleted after successful commit: %s", image_path)

    _add_commit_hook(db, _commit_delete)

    logger.info("Face embedding deleted for user %s", user_id)
