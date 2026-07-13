from fastapi import HTTPException, status


class FaceNotFoundException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No face detected in the image",
        )


class MultipleFacesDetectedException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Multiple faces detected. Please upload an image with exactly one face",
        )


class InvalidImageException(HTTPException):
    def __init__(self, detail: str = "Invalid image file") -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class UnsupportedImageException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported image format. Allowed: jpg, jpeg, png",
        )


class EmbeddingAlreadyExistsException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Face embedding already exists for this user",
        )


class EmbeddingNotFoundException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Face embedding not found. Please register your face first",
        )


class FaceModelException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Face recognition model failed to initialize",
        )
