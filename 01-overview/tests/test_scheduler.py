import pytest
from datetime import datetime
from unittest.mock import patch

from django.core.management import call_command, get_commands
from django.utils import timezone

from homework_quest.scheduler import get_due_jobs, get_scheduled_jobs, is_cron_due


def test_scheduled_jobs_are_registered():
    commands = get_commands()
    jobs = get_scheduled_jobs()
    assert len(jobs) >= 2
    for job in jobs:
        assert job["management_command"] in commands
        assert job["cron"]


@pytest.mark.parametrize(
    ("cron", "when", "expected"),
    [
        ("0 * * * *", datetime(2026, 9, 8, 14, 0), True),
        ("0 * * * *", datetime(2026, 9, 8, 14, 30), False),
        ("0 0 * * 0", datetime(2026, 9, 6, 0, 0), True),
        ("0 0 * * 0", datetime(2026, 9, 8, 0, 0), False),
        ("0 0 * * 0", datetime(2026, 9, 6, 12, 0), False),
    ],
)
def test_is_cron_due(cron, when, expected):
    assert is_cron_due(cron, when) is expected


def test_get_due_jobs_at_hourly_tick():
    when = timezone.make_aware(datetime(2026, 9, 8, 14, 0))
    due = get_due_jobs(now=when)
    assert [job["management_command"] for job in due] == ["auto_approve_chores"]


def test_get_due_jobs_at_weekly_reset():
    when = timezone.make_aware(datetime(2026, 9, 6, 0, 0))
    due = get_due_jobs(now=when)
    assert [job["management_command"] for job in due] == [
        "auto_approve_chores",
        "reset_weekly_cycle",
    ]


@pytest.mark.django_db
def test_run_scheduled_jobs_skips_weekly_reset_outside_sunday_midnight():
    """Regression: hourly cron wrapper must not fire reset_weekly_cycle every run."""
    tuesday_2pm = timezone.make_aware(datetime(2026, 9, 8, 14, 0))
    called_runs: list[list[str]] = []
    called: list[str] = []

    def track(command, *args, **kwargs):
        called.append(command)

    with patch(
        "homework_quest.management.commands.run_scheduled_jobs.call_command",
        side_effect=track,
    ):
        with patch("django.utils.timezone.now", return_value=tuesday_2pm):
            call_command("run_scheduled_jobs")
            called_runs.append(list(called))
            called.clear()
            call_command("run_scheduled_jobs")
            called_runs.append(list(called))

    assert called_runs == [["auto_approve_chores"], ["auto_approve_chores"]]
    assert all("reset_weekly_cycle" not in run for run in called_runs)


@pytest.mark.django_db
def test_scheduled_auto_approve_command_is_callable():
    call_command("auto_approve_chores")


def test_run_scheduled_jobs_command_exists():
    assert "run_scheduled_jobs" in get_commands()
