import asyncio
import logging

import numpy as np

from app.face.detector import get_model
from app.face.exceptions import FaceModelException, FaceNotFoundException, MultipleFacesDetectedException

logger = logging.getLogger(__name__)


async def generate_embedding(image: np.ndarray) -> list[float]:
    """Generate a 512-dimensional face embedding from an image.

    Runs the InsightFace inference in a thread to avoid blocking the event loop.
    Detection and embedding extraction happen in a single model call.

    Args:
        image: Decoded image as a NumPy array (BGR format from OpenCV).

    Returns:
        A list of 512 floats representing the face embedding.

    Raises:
        FaceNotFoundException: No face detected.
        MultipleFacesDetectedException: More than one face detected.
        FaceModelException: Model not initialized.
    """
    model = get_model()
    faces = await asyncio.to_thread(model.get, image)
    if not faces:
        raise FaceNotFoundException()
    if len(faces) > 1:
        raise MultipleFacesDetectedException()
    embedding = faces[0].embedding
    if embedding is None:
        logger.error("Model returned None embedding")
        raise FaceModelException()
    if hasattr(embedding, "tolist"):
        return embedding.tolist()
    return list(embedding)
