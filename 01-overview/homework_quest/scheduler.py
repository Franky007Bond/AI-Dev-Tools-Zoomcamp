"""Registered unattended jobs for Homework Quest."""

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
