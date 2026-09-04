from datetime import timedelta

import pytest
from django.test import Client
from django.utils import timezone

from homework_quest.models import Perk, Profile, WeeklyCycle


@pytest.fixture
def client():
    return Client()


@pytest.mark.django_db
def test_dashboard_includes_arcade_hooks(client):
    response = client.get("/")
    assert response.status_code == 200
    html = response.content.decode()
    assert 'data-arcade="dashboard"' in html
    assert "homework_quest/arcade.js" in html
    assert 'id="arcade-confetti"' in html


@pytest.mark.django_db
def test_ceremony_includes_arcade_hooks(client):
    perk = Perk.objects.create(title="Pizza Night", is_active=True)
    now = timezone.now()
    WeeklyCycle.objects.create(
        start_time=now - timedelta(days=1),
        end_time=now + timedelta(days=6),
        selected_perk=perk,
    )
    response = client.get("/ceremony/")
    assert response.status_code == 200
    html = response.content.decode()
    assert 'data-arcade="ceremony"' in html
    assert "homework_quest/arcade.js" in html
    assert 'id="arcade-confetti"' in html


@pytest.mark.django_db
def test_review_page_includes_arcade_hooks(client):
    response = client.get("/review-pending/")
    assert response.status_code == 200
    html = response.content.decode()
    assert 'data-arcade="review"' in html
    assert "homework_quest/arcade.js" in html


@pytest.mark.django_db
def test_arcade_js_documents_audio_fallback():
    from pathlib import Path

    arcade_js = (
        Path(__file__).resolve().parent / "static" / "homework_quest" / "arcade.js"
    ).read_text(encoding="utf-8")
    assert "AudioContext" in arcade_js
    assert "suspended" in arcade_js or "blocked" in arcade_js.lower()
