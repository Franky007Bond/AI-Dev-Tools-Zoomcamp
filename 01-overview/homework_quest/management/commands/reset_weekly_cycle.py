from django.core.management.base import BaseCommand, CommandError

from homework_quest.cycle import CycleError, close_weekly_cycle


class Command(BaseCommand):
    help = (
        "Close the current weekly cycle, record winners, reset XP, and draw the next perk. "
        "Run with: uv run python manage.py reset_weekly_cycle"
    )

    def handle(self, *args, **options):
        try:
            closed_cycle, new_cycle = close_weekly_cycle()
        except CycleError as exc:
            raise CommandError(str(exc)) from exc

        winners = closed_cycle.winner_ids
        winner_text = ", ".join(str(winner_id) for winner_id in winners) or "none"
        self.stdout.write(
            self.style.SUCCESS(
                f"Closed cycle {closed_cycle.pk} (winners: {winner_text}). "
                f"Started cycle {new_cycle.pk} with stake "
                f'"{new_cycle.selected_perk.title}".'
            )
        )
