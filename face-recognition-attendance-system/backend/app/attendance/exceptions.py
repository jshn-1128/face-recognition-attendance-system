"""Attendance module exception hierarchy.

All exceptions inherit from :class:`AttendanceException` and are
HTTP-aware (subclasses of FastAPI's ``HTTPException``) so they can
be raised directly from the router layer in future milestones.
The service layer should instantiate these and let the router — or
a dedicated exception handler — translate them to HTTP responses.
"""

from fastapi import HTTPException, status


class AttendanceException(HTTPException):
    """Base exception for all attendance-related errors.

    All attendance exceptions inherit from this class.
    """

    def __init__(
        self,
        detail: str = "Attendance error",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail)


class AttendanceAlreadyCheckedInException(AttendanceException):
    """Raised when a user attempts to check in while already checked in."""

    def __init__(self) -> None:
        super().__init__(
            detail="User is already checked in for today",
            status_code=status.HTTP_409_CONFLICT,
        )


class AttendanceAlreadyCheckedOutException(AttendanceException):
    """Raised when a user attempts to check out while already checked out."""

    def __init__(self) -> None:
        super().__init__(
            detail="User is already checked out for today",
            status_code=status.HTTP_409_CONFLICT,
        )


class AttendancePolicyViolationException(AttendanceException):
    """Raised when an attendance operation violates a business policy.

    Examples: attempting to check in outside of permitted shift hours,
    checking out before minimum working time has elapsed.
    """

    def __init__(self, detail: str = "Attendance policy violation") -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class AttendanceNotFoundException(AttendanceException):
    """Raised when no attendance record is found for the requested criteria."""

    def __init__(self) -> None:
        super().__init__(
            detail="Attendance record not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class AttendanceValidationException(AttendanceException):
    """Raised when attendance input data fails validation.

    Examples: missing required fields, invalid date range,
        malformed identifiers.
    """

    def __init__(self, detail: str = "Attendance validation error") -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
