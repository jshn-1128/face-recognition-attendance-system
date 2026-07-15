"""Attendance API router.

Defines the external API contract for the attendance subsystem.
Endpoints will be implemented in future milestones — the router
is registered with the application but exposes no routes until
the orchestration layer is ready.
"""

from fastapi import APIRouter

router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"],
)
