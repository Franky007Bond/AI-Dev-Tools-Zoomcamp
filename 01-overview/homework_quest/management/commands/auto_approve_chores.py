from django.core.management.base import BaseCommand

from homework_quest.services import auto_approve_due_chores


class Command(BaseCommand):
    help = (
        "Auto-approve pending chores whose 24-hour deadline has passed. "
        "Run with: uv run python manage.py auto_approve_chores"
    )

    def handle(self, *args, **options):
        approved_count = auto_approve_due_chores()
        self.stdout.write(
            self.style.SUCCESS(f"Auto-approved {approved_count} chore(s).")
        )
