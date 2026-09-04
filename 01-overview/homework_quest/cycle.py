"""Weekly cycle winner selection and reset for Homework Quest."""

from __future__ import annotations

import random
from datetime import datetime, timedelta

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from homework_quest.models import Perk, Profile, WeeklyCycle


class CycleError(Exception):
    pass


def select_winners(xp_by_profile_id: dict[int, int]) -> list[int]:
    """Return the unique top scorer, or every profile tied for first place."""
    if not xp_by_profile_id:
        return []
    top_xp = max(xp_by_profile_id.values())
    return [profile_id for profile_id, xp in xp_by_profile_id.items() if xp == top_xp]


def next_sunday_midnight(after: datetime) -> datetime:
    """Return the next Sunday 00:00 after ``after`` (timezone-aware)."""
    midnight = after.replace(hour=0, minute=0, second=0, microsecond=0)
    days_ahead = (6 - midnight.weekday()) % 7
    if days_ahead == 0 and after >= midnight:
        days_ahead = 7
    return midnight + timedelta(days=days_ahead)


def get_open_cycle() -> WeeklyCycle | None:
    """Return the current cycle that has not been closed yet."""
    return WeeklyCycle.objects.filter(winner_ids=[]).order_by("-start_time").first()


def close_weekly_cycle(*, now=None, rng: random.Random | None = None) -> tuple[WeeklyCycle, WeeklyCycle]:
    """Close the open cycle, record winners, reset XP, and start the next cycle."""
    now = now or timezone.now()
    rng = rng or random.Random()

    cycle = get_open_cycle()
    if cycle is None:
        raise CycleError("No open weekly cycle to close.")

    active_perks = list(Perk.objects.filter(is_active=True))
    if not active_perks:
        raise CycleError("No active perks available for the next cycle.")

    standings = {
        profile.pk: profile.current_cycle_xp
        for profile in Profile.objects.all().order_by("pk")
    }
    winners = select_winners(standings)

    with transaction.atomic():
        cycle.standings_json = standings
        cycle.winner_ids = winners
        cycle.end_time = now
        cycle.save(update_fields=["standings_json", "winner_ids", "end_time"])

        if winners:
            Profile.objects.filter(pk__in=winners).update(total_wins=F("total_wins") + 1)

        Profile.objects.update(current_cycle_xp=0)

        new_cycle = WeeklyCycle.objects.create(
            start_time=now,
            end_time=next_sunday_midnight(now),
            selected_perk=rng.choice(active_perks),
        )

    return cycle, new_cycle


def bootstrap_weekly_cycle(*, rng: random.Random | None = None) -> WeeklyCycle | None:
    """Create the first open cycle when none exists."""
    if get_open_cycle() is not None:
        return None

    rng = rng or random.Random()
    active_perks = list(Perk.objects.filter(is_active=True))
    if not active_perks:
        raise CycleError("No active perks available to bootstrap a cycle.")

    now = timezone.now()
    return WeeklyCycle.objects.create(
        start_time=now,
        end_time=next_sunday_midnight(now),
        selected_perk=rng.choice(active_perks),
    )
