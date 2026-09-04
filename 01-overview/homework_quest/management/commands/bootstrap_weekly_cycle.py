from django.core.management.base import BaseCommand, CommandError

from homework_quest.cycle import CycleError, bootstrap_weekly_cycle


class Command(BaseCommand):
    help = (
        "Create the initial weekly cycle and perk draw when none exists. "
        "Run with: uv run python manage.py bootstrap_weekly_cycle"
    )

    def handle(self, *args, **options):
        try:
            cycle = bootstrap_weekly_cycle()
        except CycleError as exc:
            raise CommandError(str(exc)) from exc

        if cycle is None:
            self.stdout.write(self.style.WARNING("An open weekly cycle already exists."))
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Bootstrapped cycle {cycle.pk} with stake "
                f'"{cycle.selected_perk.title}" until {cycle.end_time}.'
            )
        )
