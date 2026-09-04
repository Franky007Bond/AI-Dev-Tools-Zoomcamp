import pytest
from django.test import Client

from homework_quest.models import Perk, Profile


def _admin(name, pin):
    profile = Profile(name=name, pin_hash="", is_admin=True)
    profile.set_pin(pin)
    profile.save()
    return profile


@pytest.fixture
def client():
    return Client(enforce_csrf_checks=False)


def _unlock_settings(client, admin):
    return client.post(
        "/settings/unlock/",
        data={"profile_id": admin.pk, "pin": "9999"},
    )


@pytest.mark.django_db
def test_settings_perk_create_and_toggle(client):
    admin = _admin("Parent", "9999")

    gate = client.get("/settings/")
    assert gate.status_code == 200
    assert "Unlock settings" in gate.content.decode()

    unlock = _unlock_settings(client, admin)
    assert unlock.status_code == 302

    create = client.post(
        "/settings/perks/",
        data={
            "title": "Ice Cream Trip",
            "description": "Everyone gets a cone",
            "is_active": "on",
        },
    )
    assert create.status_code == 302

    perk = Perk.objects.get(title="Ice Cream Trip")
    assert perk.is_active is True
    assert perk.description == "Everyone gets a cone"

    settings_page = client.get("/settings/")
    assert settings_page.status_code == 200
    html = settings_page.content.decode()
    assert "Ice Cream Trip" in html
    assert "Active" in html

    toggle = client.post(f"/settings/perks/{perk.pk}/toggle/")
    assert toggle.status_code == 302

    perk.refresh_from_db()
    assert perk.is_active is False

    settings_page = client.get("/settings/")
    html = settings_page.content.decode()
    assert "Ice Cream Trip" in html
    assert "Inactive" in html


@pytest.mark.django_db
def test_settings_perk_create_requires_auth(client):
    response = client.post(
        "/settings/perks/",
        data={"title": "Sneaky Perk", "is_active": "on"},
    )
    assert response.status_code == 302
    assert response.url.endswith("/settings/")
    assert not Perk.objects.filter(title="Sneaky Perk").exists()
