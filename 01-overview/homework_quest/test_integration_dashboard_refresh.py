import json

import pytest
from django.test import Client

from homework_quest.models import Profile


def _profile(name, pin):
    profile = Profile(name=name, pin_hash="")
    profile.set_pin(pin)
    profile.save()
    return profile


@pytest.fixture
def client():
    return Client(enforce_csrf_checks=False)


@pytest.mark.django_db
def test_dashboard_json_shows_new_feed_item_after_log(client):
    assignee = _profile("Alex", "1234")

    before = client.get("/api/dashboard/")
    assert before.status_code == 200
    assert before.json()["feed"] == []

    client.post(
        "/api/chores/log/",
        data=json.dumps(
            {
                "profile_id": assignee.pk,
                "pin": "1234",
                "title": "Mop floor",
                "xp_value": 40,
            }
        ),
        content_type="application/json",
    )

    after = client.get("/api/dashboard/")
    payload = after.json()
    assert after.status_code == 200
    assert len(payload["feed"]) == 1
    assert payload["feed"][0]["title"] == "Mop floor"
    assert payload["feed"][0]["status_label"] == "Pending Approval"


@pytest.mark.django_db
def test_dashboard_page_includes_polling_script(client):
    response = client.get("/")
    html = response.content.decode()
    assert "dashboard.js" in html
    assert 'id="dashboard-feed"' in html
