import json
from datetime import timedelta
from unittest.mock import patch

import pytest
from django.core.management import call_command
from django.test import Client
from django.utils import timezone

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
def test_log_then_peer_approve(client):
    assignee = _profile("Alex", "1234")
    approver = _profile("Blake", "5678")

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

    approve_response = client.post(
        f"/api/chores/{chore_id}/approve/",
        data=json.dumps({"approver_id": approver.pk, "pin": "5678"}),
        content_type="application/json",
    )
    assert approve_response.status_code == 200
    assert approve_response.status_code != 500

    payload = approve_response.json()
    assignee.refresh_from_db()

    assert payload["status"] == ChoreStatus.APPROVED
    assert payload["approved_via"] == ApprovalSource.PEER
    assert assignee.current_cycle_xp == 30


@pytest.mark.django_db
def test_log_then_auto_approve_after_timeout(client):
    assignee = _profile("Alex", "1234")
    start = timezone.now()

    with patch("django.utils.timezone.now", return_value=start):
        log_response = client.post(
            "/api/chores/log/",
            data=json.dumps(
                {
                    "profile_id": assignee.pk,
                    "pin": "1234",
                    "title": "Vacuum",
                    "xp_value": 50,
                }
            ),
            content_type="application/json",
        )
    assert log_response.status_code == 201
    chore_id = log_response.json()["id"]

    with patch("django.utils.timezone.now", return_value=start + timedelta(hours=25)):
        call_command("auto_approve_chores")

    detail_response = client.get(f"/api/chores/{chore_id}/")
    assert detail_response.status_code == 200

    payload = detail_response.json()
    assignee.refresh_from_db()

    assert payload["status"] == ChoreStatus.APPROVED
    assert payload["approved_via"] == ApprovalSource.AUTO
    assert payload["approver_id"] is None
    assert assignee.current_cycle_xp == 50
