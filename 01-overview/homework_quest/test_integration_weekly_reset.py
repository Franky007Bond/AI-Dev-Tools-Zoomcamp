from datetime import timedelta

import pytest
from django.core.management import call_command
from django.utils import timezone

from homework_quest.models import Perk, Profile, WeeklyCycle


def _profile(name, pin, *, xp=0, wins=0):
    profile = Profile(name=name, pin_hash="", current_cycle_xp=xp, total_wins=wins)
    profile.set_pin(pin)
    profile.save()
    return profile


@pytest.mark.django_db
def test_week_rollover_with_tie():
    pizza = Perk.objects.create(title="Pizza Night", is_active=True)
    movie = Perk.objects.create(title="Movie Pick", is_active=True)
    inactive = Perk.objects.create(title="Old Perk", is_active=False)

    leader_a = _profile("Alex", "1234", xp=120)
    leader_b = _profile("Blake", "5678", xp=120)
    laggard = _profile("Casey", "9012", xp=40)

    now = timezone.now()
    open_cycle = WeeklyCycle.objects.create(
        start_time=now - timedelta(days=6),
        end_time=now - timedelta(hours=1),
        selected_perk=pizza,
    )

    call_command("reset_weekly_cycle")

    open_cycle.refresh_from_db()
    leader_a.refresh_from_db()
    leader_b.refresh_from_db()
    laggard.refresh_from_db()

    assert sorted(open_cycle.winner_ids) == sorted([leader_a.pk, leader_b.pk])
    assert open_cycle.standings_json == {
        str(leader_a.pk): 120,
        str(leader_b.pk): 120,
        str(laggard.pk): 40,
    }
    assert leader_a.current_cycle_xp == 0
    assert leader_b.current_cycle_xp == 0
    assert laggard.current_cycle_xp == 0
    assert leader_a.total_wins == 1
    assert leader_b.total_wins == 1
    assert laggard.total_wins == 0

    new_cycle = WeeklyCycle.objects.exclude(pk=open_cycle.pk).get()
    assert new_cycle.winner_ids == []
    assert new_cycle.selected_perk_id in {pizza.pk, movie.pk}
    assert new_cycle.selected_perk_id != inactive.pk
    assert new_cycle.start_time <= timezone.now()
    assert new_cycle.end_time > new_cycle.start_time
