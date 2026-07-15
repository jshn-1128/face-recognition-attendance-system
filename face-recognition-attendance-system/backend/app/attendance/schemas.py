"""Attendance API schemas.

Pydantic v2 models for the attendance subsystem.  These are the
**only** objects serialised to HTTP responses — internal domain
models are never exposed directly.
"""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class AttendanceResponse(BaseModel):
    """Response returned after a check-in or check-out operation.

    Contains the outcome of the operation together with the
    resulting attendance record details.
    """

    success: bool = Field(
        ...,
        description="Whether the operation completed successfully",
        examples=[True],
    )
    message: str = Field(
        ...,
        description="Human-readable outcome description",
        examples=["Successfully checked in"],
    )
    attendance_id: uuid.UUID | None = Field(
        None,
        description="Unique identifier of the attendance record",
        examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"],
    )
    user_id: uuid.UUID = Field(
        ...,
        description="UUID of the user who performed the operation",
        examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"],
    )
    status: str | None = Field(
        None,
        description="Attendance status after the operation",
        examples=["checked_in", "checked_out"],
    )
    clock_in: datetime | None = Field(
        None,
        description="Timestamp of check-in",
        examples=["2026-07-14T09:00:00"],
    )
    clock_out: datetime | None = Field(
        None,
        description="Timestamp of check-out",
        examples=["2026-07-14T18:00:00"],
    )
    working_hours: float = Field(
        0.0,
        ge=0.0,
        description="Total working hours for the day",
        examples=[8.5],
    )
    created_at: datetime | None = Field(
        None,
        description="Timestamp when the record was created",
    )
    updated_at: datetime | None = Field(
        None,
        description="Timestamp when the record was last updated",
    )


class AttendanceStatusResponse(BaseModel):
    """Current attendance status for a user.

    Lightweight response used to check whether a user is currently
    checked in or out without returning the full record.
    """

    user_id: uuid.UUID = Field(
        ...,
        description="UUID of the user",
        examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"],
    )
    status: str = Field(
        ...,
        description="Current attendance status",
        examples=["checked_in", "checked_out", "absent"],
    )
    clock_in: datetime | None = Field(
        None,
        description="Timestamp of check-in (``None`` if absent)",
        examples=["2026-07-14T09:00:00"],
    )
    elapsed_hours: float = Field(
        0.0,
        ge=0.0,
        description="Hours elapsed since check-in (0.0 if not checked in)",
        examples=[4.5],
    )
    attendance_date: date = Field(
        ...,
        description="The date this status applies to",
        examples=["2026-07-14"],
    )


class AttendanceHistoryResponse(BaseModel):
    """Paginated attendance history for a user.

    Contains a list of attendance records within the requested date
    range together with summary metadata.
    """

    records: list[AttendanceResponse] = Field(
        ...,
        description="List of attendance records ordered by date descending",
    )
    total_count: int = Field(
        ...,
        ge=0,
        description="Total number of records matching the query",
        examples=[42],
    )
    start_date: date = Field(
        ...,
        description="Inclusive start of the queried date range",
    )
    end_date: date = Field(
        ...,
        description="Inclusive end of the queried date range",
    )


class AttendanceStatisticsResponse(BaseModel):
    """Aggregated attendance statistics for a user over a period.

    Provides summary metrics useful for dashboards and reports.
    """

    user_id: uuid.UUID = Field(
        ...,
        description="UUID of the user these statistics belong to",
        examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"],
    )
    total_days: int = Field(
        ...,
        ge=0,
        description="Number of days in the analysis period",
        examples=[22],
    )
    present_days: int = Field(
        ...,
        ge=0,
        description="Number of days the user was present",
        examples=[20],
    )
    absent_days: int = Field(
        ...,
        ge=0,
        description="Number of days the user was absent",
        examples=[2],
    )
    late_days: int = Field(
        ...,
        ge=0,
        description="Number of days the user arrived late",
        examples=[3],
    )
    early_departures: int = Field(
        ...,
        ge=0,
        description="Number of days the user left early",
        examples=[1],
    )
    total_hours: float = Field(
        ...,
        ge=0.0,
        description="Total working hours in the period",
        examples=[176.0],
    )
    average_hours_per_day: float = Field(
        ...,
        ge=0.0,
        description="Average working hours per day",
        examples=[8.0],
    )
    attendance_percentage: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Attendance rate as a percentage",
        examples=[90.91],
    )
    start_date: date = Field(
        ...,
        description="Inclusive start of the analysis period",
    )
    end_date: date = Field(
        ...,
        description="Inclusive end of the analysis period",
    )
