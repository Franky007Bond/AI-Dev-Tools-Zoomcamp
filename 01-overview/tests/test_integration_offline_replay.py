import json

import pytest
from django.test import Client

from homework_quest.models import ApprovalSource, ChoreStatus, Profile
from homework_quest.offline_queue import validate_queue_item


def _profile(name, pin):
    profile = Profile(name=name, pin_hash="")
    profile.set_pin(pin)
    profile.save()
    return profile


@pytest.fixture
def client():
    return Client(enforce_csrf_checks=False)


@pytest.mark.django_db
def test_replayed_offline_approve_post_is_accepted(client):
    """Simulates flushing a queued approve payload against the API."""
    assignee = _profile("Alex", "1234")
    approver = _profile("Blake", "5678")

    log_response = client.post(
        "/api/chores/log/",
        data=json.dumps(
            {
                "profile_id": assignee.pk,
                "pin": "1234",
                "title": "Dishes",
                "estimated_minutes": 14,
            }
        ),
        content_type="application/json",
    )
    chore_id = log_response.json()["id"]

    item = validate_queue_item(
        {
            "kind": "approve",
            "url": f"/api/chores/{chore_id}/approve/",
            "contentType": "json",
            "body": {"approver_id": approver.pk, "pin": "5678"},
        }
    )

    replay = client.post(
        item["url"],
        data=json.dumps(item["body"]),
        content_type="application/json",
    )
    assert replay.status_code == 200
    assert replay.json()["status"] == ChoreStatus.APPROVED
    assert replay.json()["approved_via"] == ApprovalSource.PEER
