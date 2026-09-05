from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from homework_quest.scheduler import get_due_jobs


class Command(BaseCommand):
    help = (
        "Run scheduled Homework Quest jobs that are due at the current time (for cron). "
        "Each job's cadence is defined in homework_quest/scheduler.py. "
        "Run with: uv run python manage.py run_scheduled_jobs"
    )

    def handle(self, *args, **options):
        now = timezone.now()
        due_jobs = get_due_jobs(now=now)
        if not due_jobs:
            self.stdout.write("No scheduled jobs due at this time.")
            return

        for job in due_jobs:
            command = job["management_command"]
            self.stdout.write(f"Running {command} …")
            try:
                call_command(command)
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f"{command} failed: {exc}"))
