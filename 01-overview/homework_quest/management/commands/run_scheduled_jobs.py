from django.core.management import call_command
from django.core.management.base import BaseCommand

from homework_quest.scheduler import get_scheduled_jobs


class Command(BaseCommand):
    help = (
        "Run all scheduled Homework Quest jobs (for cron wrappers). "
        "Run with: uv run python manage.py run_scheduled_jobs"
    )

    def handle(self, *args, **options):
        for job in get_scheduled_jobs():
            command = job["management_command"]
            self.stdout.write(f"Running {command} …")
            try:
                call_command(command)
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f"{command} failed: {exc}"))
