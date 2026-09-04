import pytest
from django.core.management import call_command, get_commands

from homework_quest.scheduler import get_scheduled_jobs


def test_scheduled_jobs_are_registered():
    commands = get_commands()
    jobs = get_scheduled_jobs()
    assert len(jobs) >= 2
    for job in jobs:
        assert job["management_command"] in commands
        assert job["cron"]


@pytest.mark.django_db
def test_scheduled_auto_approve_command_is_callable():
    call_command("auto_approve_chores")


def test_run_scheduled_jobs_command_exists():
    assert "run_scheduled_jobs" in get_commands()
