"""Attendance repository — data-access layer for attendance records.

The repository encapsulates all database interactions for the
attendance subsystem.  It returns immutable domain objects and
raises repository-level exceptions.  No business logic, no HTTP
concerns, and no AI operations exist in this layer.
"""

import uuid
from collections.abc import Sequence
from datetime import date, datetime


# ======================================================================
# Repository-level exceptions
# ======================================================================


class RepositoryError(Exception):
    """Base exception for all attendance-repository errors.

    Raised when a database operation fails unexpectedly.
    """


# ======================================================================
# Repository
# ======================================================================


class AttendanceRepository:
    """Data-access layer for attendance records.

    Every public method requires the relevant identifiers or filter
    parameters — no sessions are managed internally.  Implementations
    will be provided in a future milestone.
    """

    async def create_attendance(
        self,
        user_id: uuid.UUID,
    ) -> object:
        """Create a new attendance record for today.

        Args:
            user_id: UUID of the user creating the record.

        Returns:
            The newly created attendance record.

        Raises:
            NotImplementedError: This method is a stub and will be
                implemented in a future milestone.
        """
        raise NotImplementedError(
            "AttendanceRepository.create_attendance will be implemented "
            "in a future milestone"
        )

    async def update_attendance(
        self,
        attendance_id: uuid.UUID,
        **kwargs: object,
    ) -> object:
        """Update an existing attendance record.

        Args:
            attendance_id: UUID of the record to update.
            **kwargs: Fields to update (e.g. ``clock_out``).

        Returns:
            The updated attendance record.

        Raises:
            NotImplementedError: This method is a stub and will be
                implemented in a future milestone.
        """
        raise NotImplementedError(
            "AttendanceRepository.update_attendance will be implemented "
            "in a future milestone"
        )

    async def get_today(
        self,
        user_id: uuid.UUID,
    ) -> object | None:
        """Retrieve today's attendance record for a user.

        Args:
            user_id: UUID of the user whose record to retrieve.

        Returns:
            The attendance record for today, or ``None`` if the user
            has no record for today.

        Raises:
            NotImplementedError: This method is a stub and will be
                implemented in a future milestone.
        """
        raise NotImplementedError(
            "AttendanceRepository.get_today will be implemented "
            "in a future milestone"
        )

    async def get_history(
        self,
        user_id: uuid.UUID,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> Sequence[object]:
        """Retrieve attendance history for a user within a date range.

        Args:
            user_id: UUID of the user whose history to retrieve.
            start_date: Inclusive start of the range (``None`` for
                no lower bound).
            end_date: Inclusive end of the range (``None`` for
                no upper bound).

        Returns:
            A sequence of attendance records ordered by date descending.

        Raises:
            NotImplementedError: This method is a stub and will be
                implemented in a future milestone.
        """
        raise NotImplementedError(
            "AttendanceRepository.get_history will be implemented "
            "in a future milestone"
        )

    async def get_statistics(
        self,
        user_id: uuid.UUID,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> object:
        """Return aggregated attendance statistics for a user.

        Args:
            user_id: UUID of the user whose statistics to compute.
            start_date: Inclusive start of the analysis period.
            end_date: Inclusive end of the analysis period.

        Returns:
            An object containing aggregated statistics.

        Raises:
            NotImplementedError: This method is a stub and will be
                implemented in a future milestone.
        """
        raise NotImplementedError(
            "AttendanceRepository.get_statistics will be implemented "
            "in a future milestone"
        )

    async def attendance_exists(
        self,
        user_id: uuid.UUID,
        target_date: date | None = None,
    ) -> bool:
        """Check whether an attendance record exists for a given date.

        Args:
            user_id: UUID of the user to check.
            target_date: The date to check (``None`` for today).

        Returns:
            ``True`` if a record exists for the given date.

        Raises:
            NotImplementedError: This method is a stub and will be
                implemented in a future milestone.
        """
        raise NotImplementedError(
            "AttendanceRepository.attendance_exists will be implemented "
            "in a future milestone"
        )
