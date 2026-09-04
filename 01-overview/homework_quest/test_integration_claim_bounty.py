import pytest
from django.test import Client

from homework_quest.models import ChoreInstance, ChoreStatus, Profile
from homework_quest.services import create_adhoc_bounty


def _profile(name, pin):
    profile = Profile(name=name, pin_hash="")
    profile.set_pin(pin)
    profile.save()
    return profile


@pytest.fixture
def client():
    return Client(enforce_csrf_checks=False)


@pytest.mark.django_db
def test_claimed_bounty_appears_in_review_queue(client):
    poster = _profile("Alex", "1234")
    claimer = _profile("Blake", "5678")

    bounty = create_adhoc_bounty(title="Clean garage", _category="Outdoor", estimated_minutes=25)
    assert bounty.status == ChoreStatus.OPEN

    claim = client.post(
        f"/chore-pool/log-bounty/{bounty.pk}/",
        data={"profile_id": claimer.pk, "pin": "5678"},
    )
    assert claim.status_code == 302

    bounty.refresh_from_db()
    assert bounty.status == ChoreStatus.PENDING
    assert bounty.assignee_id == claimer.pk

    review = client.get("/review-pending/")
    html = review.content.decode()
    assert "Clean garage" in html
    assert poster.name not in html or "Clean garage" in html
