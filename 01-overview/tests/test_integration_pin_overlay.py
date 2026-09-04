import json

import pytest
from django.test import Client

from homework_quest.models import ApprovalSource, ChoreStatus, Profile


def _profile(name, pin):
    profile = Profile(name=name, pin_hash="")
    profile.set_pin(pin)
    profile.save()
    return profile


@pytest.fixture
def client():
    return Client(enforce_csrf_checks=False)


@pytest.mark.django_db
def test_self_approve_fails_peer_approve_succeeds(client):
    """Same POST endpoints the PIN overlay uses for approval."""
    assignee = _profile("Alex", "1234")
    peer = _profile("Blake", "5678")

    log_response = client.post(
        "/api/chores/log/",
        data=json.dumps(
            {
                "profile_id": assignee.pk,
                "pin": "1234",
                "title": "Dishes",
                "xp_value": 30,
            }
        ),
        content_type="application/json",
    )
    assert log_response.status_code == 201
    chore_id = log_response.json()["id"]

    self_approve = client.post(
        f"/api/chores/{chore_id}/approve/",
        data=json.dumps({"approver_id": assignee.pk, "pin": "1234"}),
        content_type="application/json",
    )
    assert self_approve.status_code == 400
    assert "own chore" in self_approve.json()["error"].lower()

    assignee.refresh_from_db()
    assert assignee.current_cycle_xp == 0

    peer_approve = client.post(
        f"/api/chores/{chore_id}/approve/",
        data=json.dumps({"approver_id": peer.pk, "pin": "5678"}),
        content_type="application/json",
    )
    assert peer_approve.status_code == 200

    payload = peer_approve.json()
    assignee.refresh_from_db()

    assert payload["status"] == ChoreStatus.APPROVED
    assert payload["approved_via"] == ApprovalSource.PEER
    assert assignee.current_cycle_xp == 30


@pytest.mark.django_db
def test_review_page_includes_pin_overlay(client):
    response = client.get("/review-pending/")
    assert response.status_code == 200
    html = response.content.decode()
    assert 'id="pin-overlay"' in html
    assert "pin-overlay__keypad" in html
    assert "data-pin-overlay" in html
