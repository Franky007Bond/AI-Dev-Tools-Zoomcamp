from datetime import timedelta

import pytest
from django.test import Client
from django.utils import timezone

from homework_quest.models import ApprovalSource, ChoreInstance, ChoreStatus, Perk, Profile, WeeklyCycle


def _profile(name, pin, *, xp=0):
    profile = Profile(name=name, pin_hash="", current_cycle_xp=xp)
    profile.set_pin(pin)
    profile.save()
    return profile


@pytest.fixture
def client():
    return Client()


@pytest.mark.django_db
def test_dashboard_shows_standings_and_feed(client):
    alex = _profile("Alex", "1234", xp=90)
    blake = _profile("Blake", "5678", xp=120)
    perk = Perk.objects.create(title="Pizza Night", is_active=True)
    now = timezone.now()
    WeeklyCycle.objects.create(
        start_time=now - timedelta(days=2),
        end_time=now + timedelta(days=5),
        selected_perk=perk,
    )

    pending = ChoreInstance(title="Dishes", xp_value=30, assignee=alex)
    pending.mark_pending(submitted_at=now - timedelta(hours=2))
    pending.save()

    verified = ChoreInstance(title="Vacuum", xp_value=50, assignee=blake)
    verified.mark_pending(submitted_at=now - timedelta(hours=5))
    verified.approve(approver=alex, via=ApprovalSource.PEER)
    verified.save()

    response = client.get("/")

    assert response.status_code == 200
    html = response.content.decode()

    assert "Blake" in html
    assert "Alex" in html
    assert "120 XP" in html
    assert "90 XP" in html
    assert "Pizza Night" in html
    assert "Dishes" in html
    assert "Vacuum" in html
    assert "Pending Approval" in html
    assert "Verified" in html
