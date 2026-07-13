import logging

import numpy as np

from app.face.detector import get_model, validate_single_face
from app.face.exceptions import FaceModelException

logger = logging.getLogger(__name__)


def generate_embedding(image: np.ndarray) -> list[float]:
    """Generate a 512-dimensional face embedding from an image.

    Args:
        image: Decoded image as a NumPy array (BGR format from OpenCV).

    Returns:
        A list of 512 floats representing the face embedding.

    Raises:
        FaceNotFoundException: No face detected.
        MultipleFacesDetectedException: More than one face detected.
        FaceModelException: Model not initialized.
    """
    validate_single_face(image)
    model = get_model()
    faces = model.get(image)
    if not faces:
        from app.face.exceptions import FaceNotFoundException
        raise FaceNotFoundException()
    embedding = faces[0].embedding
    if embedding is None:
        logger.error("Model returned None embedding")
        raise FaceModelException()
    if hasattr(embedding, "tolist"):
        return embedding.tolist()
    return list(embedding)
