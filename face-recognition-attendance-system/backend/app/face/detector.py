import asyncio
import logging

import cv2
import numpy as np

from app.face.exceptions import (
    FaceModelException,
    FaceNotFoundException,
    MultipleFacesDetectedException,
)

logger = logging.getLogger(__name__)

_model = None


def initialize(model_name: str = "buffalo_l") -> None:
    """Load InsightFace model once and cache it."""
    global _model
    if _model is not None:
        return
    try:
        import insightface
        from insightface.app import FaceAnalysis
        app = FaceAnalysis(name=model_name, providers=["CPUExecutionProvider"])
        app.prepare(ctx_id=0, det_size=(640, 640))
        _model = app
        logger.info("Face model '%s' initialized successfully", model_name)
    except Exception as exc:
        logger.error("Failed to initialize face model '%s': %s", model_name, exc)
        raise FaceModelException() from exc


def get_model():
    """Return the cached InsightFace model instance."""
    if _model is None:
        raise FaceModelException()
    return _model


def _extract_landmarks(face) -> list | None:
    """Extract face landmarks safely across InsightFace versions.

    Different InsightFace versions expose landmarks under different attribute
    names. This function tries all known variants and returns ``None`` when
    landmarks are unavailable.

    Args:
        face: An InsightFace ``Face`` object from ``FaceAnalysis.get()``.

    Returns:
        A list of landmark coordinates, or ``None`` when no landmarks exist.
    """
    landmarks_attr = None
    source = None

    for attr_name in ("kps", "landmarks"):
        attr = getattr(face, attr_name, None)
        if attr is not None:
            landmarks_attr = attr
            source = attr_name
            break

    if landmarks_attr is None:
        logger.debug("Face landmarks unavailable (checked: kps, landmarks)")
        return None

    logger.debug("Face landmarks extracted from '%s'", source)
    if hasattr(landmarks_attr, "tolist"):
        return landmarks_attr.tolist()
    return list(landmarks_attr)


def detect_faces(image: np.ndarray) -> list[dict]:
    """Detect faces in the image and return bounding boxes, landmarks, and confidence."""
    model = get_model()
    faces = model.get(image)
    results = []
    for face in faces:
        results.append({
            "bbox": face.bbox.tolist() if hasattr(face.bbox, "tolist") else list(face.bbox),
            "landmarks": _extract_landmarks(face),
            "confidence": float(face.det_score),
        })
    return results


def validate_single_face(image: np.ndarray) -> dict:
    """Detect exactly one face in the image and return its details.

    Raises:
        FaceNotFoundException: No face detected.
        MultipleFacesDetectedException: More than one face detected.
    """
    faces = detect_faces(image)
    if not faces:
        raise FaceNotFoundException()
    if len(faces) > 1:
        raise MultipleFacesDetectedException()
    return faces[0]


async def read_image_from_bytes(image_bytes: bytes) -> np.ndarray:
    """Decode raw bytes into an OpenCV image array (offloaded to thread)."""
    np_arr = np.frombuffer(image_bytes, dtype=np.uint8)
    image = await asyncio.to_thread(cv2.imdecode, np_arr, cv2.IMREAD_COLOR)
    if image is None:
        from app.face.exceptions import InvalidImageException
        raise InvalidImageException("Could not decode image. The file may be corrupted")
    return image
