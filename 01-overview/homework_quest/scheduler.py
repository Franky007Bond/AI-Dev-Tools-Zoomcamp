"""Registered unattended jobs for Homework Quest."""

from __future__ import annotations

from datetime import datetime

from django.utils import timezone

SCHEDULED_JOBS = (
    {
        "name": "auto_approve_chores",
        "management_command": "auto_approve_chores",
        "cron": "0 * * * *",
        "description": "Hourly auto-approve for pending chores past 24 hours.",
    },
    {
        "name": "reset_weekly_cycle",
        "management_command": "reset_weekly_cycle",
        "cron": "0 0 * * 0",
        "description": "Weekly reset every Sunday at 00:00.",
    },
)


def get_scheduled_jobs() -> tuple[dict, ...]:
    return SCHEDULED_JOBS


def _cron_field_matches(field: str, value: int) -> bool:
    if field == "*":
        return True
    return int(field) == value


def _cron_day_of_week_matches(field: str, when: datetime) -> bool:
    if field == "*":
        return True
    # Cron: 0 or 7 = Sunday; Python weekday(): Monday=0 .. Sunday=6.
    cron_dow = (when.weekday() + 1) % 7
    expected = int(field)
    if expected == 7:
        expected = 0
    return cron_dow == expected


def is_cron_due(cron: str, when: datetime) -> bool:
    """Return True when ``when`` matches a standard five-field cron schedule."""
    parts = cron.split()
    if len(parts) != 5:
        raise ValueError(f"Unsupported cron expression: {cron!r}")
    minute, hour, day_of_month, month, day_of_week = parts
    return (
        _cron_field_matches(minute, when.minute)
        and _cron_field_matches(hour, when.hour)
        and _cron_field_matches(day_of_month, when.day)
        and _cron_field_matches(month, when.month)
        and _cron_day_of_week_matches(day_of_week, when)
    )


def get_due_jobs(now: datetime | None = None) -> tuple[dict, ...]:
    """Return scheduled jobs whose cron expression matches ``now`` (minute precision)."""
    now = now or timezone.now()
    return tuple(job for job in get_scheduled_jobs() if is_cron_due(job["cron"], now))
