"""Attendance database model.

SQLAlchemy 2.x declarative model for the attendance subsystem.
Stores daily attendance records linked to the users table.
"""

import enum
import uuid
from datetime import date, datetime

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class AttendanceStatus(str, enum.Enum):
    """Enumeration of possible attendance statuses for a single day."""

    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    HALF_DAY = "half_day"
    ON_LEAVE = "on_leave"


class AttendanceMethod(str, enum.Enum):
    """Enumeration of methods by which attendance can be recorded."""

    FACE = "face"
    MANUAL = "manual"
    ADMIN = "admin"
    IMPORT = "import"


class Attendance(Base):
    """Daily attendance record for a user.

    Each row represents one employee's attendance for a single day.
    A unique constraint on (user_id, attendance_date) enforces the
    business rule of one record per employee per day.
    """

    __tablename__ = "attendance"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    attendance_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    clock_in: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    clock_out: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    status: Mapped[AttendanceStatus] = mapped_column(
        Enum(AttendanceStatus, name="attendance_status", create_constraint=True),
        nullable=False,
        default=AttendanceStatus.PRESENT,
    )
    method: Mapped[AttendanceMethod] = mapped_column(
        Enum(AttendanceMethod, name="attendance_method", create_constraint=True),
        nullable=False,
        default=AttendanceMethod.FACE,
    )
    recognition_confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    verification_confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        backref="attendance_records",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "attendance_date",
            name="uq_attendance_user_date",
        ),
        CheckConstraint(
            "recognition_confidence >= 0 AND recognition_confidence <= 100",
            name="ck_attendance_recognition_confidence_range",
        ),
        CheckConstraint(
            "verification_confidence >= 0 AND verification_confidence <= 100",
            name="ck_attendance_verification_confidence_range",
        ),
        Index("ix_attendance_user_id", "user_id"),
        Index("ix_attendance_attendance_date", "attendance_date"),
        Index("ix_attendance_status", "status"),
        Index("ix_attendance_method", "method"),
        Index("ix_attendance_clock_in", "clock_in"),
    )

    def __repr__(self) -> str:
        return (
            f"Attendance("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"attendance_date={self.attendance_date}"
            f")"
        )
