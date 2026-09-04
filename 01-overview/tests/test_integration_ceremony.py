from datetime import timedelta

import pytest
from django.test import Client
from django.utils import timezone

from homework_quest.models import Perk, Profile, WeeklyCycle


def _profile(name, pin, *, xp=0):
    profile = Profile(name=name, pin_hash="", current_cycle_xp=xp)
    profile.set_pin(pin)
    profile.save()
    return profile


@pytest.fixture
def client():
    return Client(enforce_csrf_checks=False)


@pytest.mark.django_db
def test_ceremony_shows_standings_and_start_button(client):
    alex = _profile("Alex", "1234", xp=80)
    _profile("Blake", "5678", xp=120)
    perk = Perk.objects.create(title="Pizza Night", is_active=True)
    now = timezone.now()
    WeeklyCycle.objects.create(
        start_time=now - timedelta(days=3),
        end_time=now + timedelta(days=4),
        selected_perk=perk,
    )

    response = client.get("/ceremony/")
    assert response.status_code == 200
    html = response.content.decode()

    assert "Weekly Ceremony" in html
    assert "Alex" in html
    assert "Blake" in html
    assert "Start New Cycle" in html
    assert "Pizza Night" in html


@pytest.mark.django_db
def test_ceremony_start_new_cycle_runs_reset(client):
    pizza = Perk.objects.create(title="Pizza Night", is_active=True)
    movie = Perk.objects.create(title="Movie Pick", is_active=True)
    leader = _profile("Alex", "1234", xp=100)
    now = timezone.now()
    WeeklyCycle.objects.create(
        start_time=now - timedelta(days=6),
        end_time=now - timedelta(hours=1),
        selected_perk=pizza,
    )

    response = client.post("/ceremony/start/")
    assert response.status_code == 302
    assert response.url.endswith("/ceremony/?reset=1")

    leader.refresh_from_db()
    assert leader.current_cycle_xp == 0
    assert leader.total_wins == 1

    celebration = client.get("/ceremony/?reset=1")
    html = celebration.content.decode()
    assert "Week complete" in html
    assert "Start New Cycle" in html
    assert movie.title in html or pizza.title in html

    assert WeeklyCycle.objects.filter(winner_ids=[]).count() == 1
    assert WeeklyCycle.objects.exclude(winner_ids=[]).count() == 1
