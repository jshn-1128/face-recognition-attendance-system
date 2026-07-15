"""Attendance service — orchestrates the attendance pipeline.

The service is the bridge between HTTP (via the router), the
:class:`AttendanceRepository` (data access), and the
:class:`AttendancePolicyEngine` (business rules).  It performs
**no** SQL, file I/O, or AI operations directly — it delegates
everything to injected dependencies.
"""

import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, datetime

from app.attendance.repository import AttendanceRepository


# ======================================================================
# Domain model
# ======================================================================


@dataclass(frozen=True)
class AttendanceResult:
    """Immutable result of an attendance operation.

    This is the **only** domain object returned by the service layer.
    Consumers (routers, reports, analytics) receive this object and
    never interact with repository models or raw database rows directly.

    Attributes:
        success: Whether the operation completed successfully.
        message: Human-readable outcome description.
        attendance_id: Unique identifier of the attendance record.
        user_id: UUID of the user who performed the operation.
        status: Current attendance status (e.g. ``"checked_in"``,
            ``"checked_out"``).
        clock_in: Timestamp when the user checked in (``None`` if
            not yet checked in).
        clock_out: Timestamp when the user checked out (``None`` if
            not yet checked out).
        working_hours: Total working hours as a ``float`` (``0.0``
            when unavailable).
        created_at: Timestamp when the record was created.
        updated_at: Timestamp when the record was last updated.
    """

    success: bool
    message: str
    attendance_id: uuid.UUID | None
    user_id: uuid.UUID | None
    status: str | None
    clock_in: datetime | None
    clock_out: datetime | None
    working_hours: float
    created_at: datetime | None
    updated_at: datetime | None


# ======================================================================
# Service
# ======================================================================


class AttendanceService:
    """Orchestrates attendance workflows.

    The service delegates data access to the :class:`AttendanceRepository`
    and business-rule evaluation to the :class:`AttendancePolicyEngine`
    (injected at construction time).

    The service is **stateless** — no mutable instance state is
    maintained across calls — and is safe for concurrent use with
    separate database sessions.
    """

    def __init__(
        self,
        repository: AttendanceRepository | None = None,
    ) -> None:
        self._repository = repository or AttendanceRepository()

    async def check_in(
        self,
        user_id: uuid.UUID,
    ) -> AttendanceResult:
        """Check in the specified user.

        Records the start of a working session for *user_id* at the
        current server time.  Business rules (shift eligibility,
        duplicate check-in prevention) are evaluated by the policy
        engine before the record is persisted.

        Args:
            user_id: UUID of the user checking in.

        Returns:
            An :class:`AttendanceResult` describing the outcome.

        Raises:
            NotImplementedError: This method is a stub and will be
                implemented in a future milestone.
        """
        raise NotImplementedError(
            "AttendanceService.check_in will be implemented in a future milestone"
        )

    async def check_out(
        self,
        user_id: uuid.UUID,
    ) -> AttendanceResult:
        """Check out the specified user.

        Records the end of a working session for *user_id* at the
        current server time.  The policy engine validates that the
        user is currently checked in and that the duration satisfies
        minimum-working-time requirements.

        Args:
            user_id: UUID of the user checking out.

        Returns:
            An :class:`AttendanceResult` describing the outcome.

        Raises:
            NotImplementedError: This method is a stub and will be
                implemented in a future milestone.
        """
        raise NotImplementedError(
            "AttendanceService.check_out will be implemented in a future milestone"
        )

    async def today_status(
        self,
        user_id: uuid.UUID,
    ) -> AttendanceResult:
        """Return today's attendance status for the specified user.

        Indicates whether the user is checked in, checked out, or
        has no record for today.

        Args:
            user_id: UUID of the user whose status to retrieve.

        Returns:
            An :class:`AttendanceResult` with the current day's
                attendance information.

        Raises:
            NotImplementedError: This method is a stub and will be
                implemented in a future milestone.
        """
        raise NotImplementedError(
            "AttendanceService.today_status will be implemented in a future milestone"
        )

    async def history(
        self,
        user_id: uuid.UUID,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> Sequence[AttendanceResult]:
        """Return the attendance history for the specified user.

        Results can be filtered by an optional date range.  When
        *start_date* and *end_date* are ``None``, a sensible default
        (e.g. the last 30 days) is used.

        Args:
            user_id: UUID of the user whose history to retrieve.
            start_date: Inclusive start of the date range (``None``
                for default).
            end_date: Inclusive end of the date range (``None`` for
                default).

        Returns:
            A sequence of :class:`AttendanceResult` records ordered
                by date descending.

        Raises:
            NotImplementedError: This method is a stub and will be
                implemented in a future milestone.
        """
        raise NotImplementedError(
            "AttendanceService.history will be implemented in a future milestone"
        )

    async def statistics(
        self,
        user_id: uuid.UUID,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> AttendanceResult:
        """Return attendance statistics for the specified user.

        Aggregates data such as total working hours, average hours
        per day, on-time percentage, and late counts over the
        requested period.

        Args:
            user_id: UUID of the user whose statistics to compute.
            start_date: Inclusive start of the analysis period
                (``None`` for default).
            end_date: Inclusive end of the analysis period (``None``
                for default).

        Returns:
            An :class:`AttendanceResult` containing aggregated
                statistics.

        Raises:
            NotImplementedError: This method is a stub and will be
                implemented in a future milestone.
        """
        raise NotImplementedError(
            "AttendanceService.statistics will be implemented in a future milestone"
        )
