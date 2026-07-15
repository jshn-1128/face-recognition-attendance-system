"""Attendance policy engine — business rules for attendance operations.

This module is a **pure** policy layer with zero dependencies on
the web framework, ORM, or database.  Every method evaluates a
single business rule and returns a boolean decision or a computed
value.  The :class:`AttendancePolicyEngine` composes these rules
into higher-level checks used by the service layer.

Policies are stateless and safe for concurrent use.
"""

import uuid
from datetime import date, datetime


class AttendancePolicyEngine:
    """Evaluates attendance business rules.

    Each method encapsulates exactly one policy concern.  Policies
    receive only the data they need — never HTTP requests, database
    sessions, or framework objects.
    """

    async def can_check_in(
        self,
        user_id: uuid.UUID,
        current_time: datetime | None = None,
    ) -> bool:
        """Determine whether a user is allowed to check in now.

        Evaluates shift eligibility, permitted check-in windows,
        and whether the user has already checked in today.

        Args:
            user_id: UUID of the user requesting check-in.
            current_time: The timestamp to evaluate (``None`` for
                the current server time).

        Returns:
            ``True`` if check-in is permitted.

        Raises:
            NotImplementedError: This method is a stub and will be
                implemented in a future milestone.
        """
        raise NotImplementedError(
            "AttendancePolicyEngine.can_check_in will be implemented "
            "in a future milestone"
        )

    async def can_check_out(
        self,
        user_id: uuid.UUID,
        current_time: datetime | None = None,
    ) -> bool:
        """Determine whether a user is allowed to check out now.

        Validates that the user is currently checked in and that the
        elapsed working time meets minimum-duration requirements.

        Args:
            user_id: UUID of the user requesting check-out.
            current_time: The timestamp to evaluate (``None`` for
                the current server time).

        Returns:
            ``True`` if check-out is permitted.

        Raises:
            NotImplementedError: This method is a stub and will be
                implemented in a future milestone.
        """
        raise NotImplementedError(
            "AttendancePolicyEngine.can_check_out will be implemented "
            "in a future milestone"
        )

    async def calculate_status(
        self,
        clock_in: datetime | None,
        clock_out: datetime | None,
    ) -> str:
        """Derive the attendance status from clock-in/out timestamps.

        Possible returned values: ``"checked_in"``, ``"checked_out"``,
        ``"absent"``, ``"late"``, ``"early_departure"``.

        Args:
            clock_in: The user's check-in timestamp (``None`` if not
                checked in).
            clock_out: The user's check-out timestamp (``None`` if not
                checked out).

        Returns:
            A string describing the current attendance status.

        Raises:
            NotImplementedError: This method is a stub and will be
                implemented in a future milestone.
        """
        raise NotImplementedError(
            "AttendancePolicyEngine.calculate_status will be implemented "
            "in a future milestone"
        )

    async def calculate_working_hours(
        self,
        clock_in: datetime,
        clock_out: datetime | None = None,
    ) -> float:
        """Calculate the total working hours from clock-in/out times.

        When *clock_out* is ``None`` the calculation is based on the
        current server time (the user is still checked in).

        Args:
            clock_in: The check-in timestamp.
            clock_out: The check-out timestamp (``None`` if still
                checked in).

        Returns:
            Total working hours as a ``float``.

        Raises:
            NotImplementedError: This method is a stub and will be
                implemented in a future milestone.
        """
        raise NotImplementedError(
            "AttendancePolicyEngine.calculate_working_hours will be "
            "implemented in a future milestone"
        )

    async def validate_shift(
        self,
        user_id: uuid.UUID,
        target_date: date | None = None,
    ) -> dict:
        """Return the shift configuration for a user on a given date.

        Returns a dict with shift metadata such as ``start_time``,
        ``end_time``, ``grace_period_minutes``, and
        ``minimum_hours``.

        Args:
            user_id: UUID of the user whose shift to look up.
            target_date: The date to check (``None`` for today).

        Returns:
            A dict describing the shift configuration.

        Raises:
            NotImplementedError: This method is a stub and will be
                implemented in a future milestone.
        """
        raise NotImplementedError(
            "AttendancePolicyEngine.validate_shift will be implemented "
            "in a future milestone"
        )
