from datetime import timedelta

import pytest
from django.core.management import call_command
from django.utils import timezone

from homework_quest.cycle import get_open_cycle
from homework_quest.models import Perk, WeeklyCycle


@pytest.mark.django_db
def test_bootstrap_creates_first_cycle():
    pizza = Perk.objects.create(title="Pizza Night", is_active=True)
    assert get_open_cycle() is None

    call_command("bootstrap_weekly_cycle")

    cycle = get_open_cycle()
    assert cycle is not None
    assert cycle.selected_perk_id == pizza.pk
    assert cycle.end_time > cycle.start_time
    assert cycle.winner_ids == []


@pytest.mark.django_db
def test_bootstrap_is_idempotent():
    perk = Perk.objects.create(title="Movie Pick", is_active=True)
    now = timezone.now()
    existing = WeeklyCycle.objects.create(
        start_time=now - timedelta(days=1),
        end_time=now + timedelta(days=5),
        selected_perk=perk,
    )

    call_command("bootstrap_weekly_cycle")

    assert WeeklyCycle.objects.count() == 1
    assert get_open_cycle().pk == existing.pk
