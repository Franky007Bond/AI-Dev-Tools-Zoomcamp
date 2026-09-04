from datetime import timedelta

import pytest
from django.test import Client
from django.utils import timezone

from homework_quest.models import ApprovalSource, ChoreInstance, Profile


def _profile(name, pin):
    profile = Profile(name=name, pin_hash="")
    profile.set_pin(pin)
    profile.save()
    return profile


@pytest.fixture
def client():
    return Client()


@pytest.mark.django_db
def test_review_queue_lists_only_pending_chores(client):
    assignee = _profile("Alex", "1234")
    approver = _profile("Blake", "5678")
    now = timezone.now()

    pending = ChoreInstance(title="Dishes", xp_value=30, assignee=assignee)
    pending.mark_pending(submitted_at=now - timedelta(hours=2))
    pending.save()

    approved = ChoreInstance(title="Vacuum", xp_value=50, assignee=assignee)
    approved.mark_pending(submitted_at=now - timedelta(hours=5))
    approved.approve(approver=approver, via=ApprovalSource.PEER)
    approved.save()

    response = client.get("/review-pending/")
    assert response.status_code == 200

    html = response.content.decode()
    assert "Dishes" in html
    assert "Vacuum" not in html
    assert "Pending Approval" not in html  # queue page, not dashboard badges
    assert "Approve" in html
    assert "24-hour" in html or "24" in html
