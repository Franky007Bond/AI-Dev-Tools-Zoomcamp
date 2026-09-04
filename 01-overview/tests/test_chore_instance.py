from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from homework_quest.models import ApprovalSource, ChoreInstance, ChoreStatus, Profile


@pytest.fixture
def profile(db):
    member = Profile(name="Alex", pin_hash="")
    member.set_pin("1234")
    member.save()
    return member


@pytest.fixture
def approver(db):
    member = Profile(name="Blake", pin_hash="")
    member.set_pin("5678")
    member.save()
    return member


@pytest.mark.django_db
def test_pending_chore_gets_twenty_four_hour_auto_approve_deadline(profile):
    submitted_at = timezone.now()
    chore = ChoreInstance(
        title="Dishes",
        xp_value=10,
        assignee=profile,
    )
    chore.mark_pending(submitted_at=submitted_at)
    chore.save()

    assert chore.status == ChoreStatus.PENDING
    assert chore.auto_approve_at == submitted_at + timedelta(hours=24)


@pytest.mark.django_db
def test_approved_chore_cannot_be_submitted_again(profile):
    chore = ChoreInstance(
        title="Dishes",
        xp_value=10,
        status=ChoreStatus.APPROVED,
        assignee=profile,
        approved_via=ApprovalSource.PEER,
    )
    chore.save()

    with pytest.raises(ValidationError, match="cannot be submitted again"):
        chore.mark_pending()


@pytest.mark.django_db
def test_approved_chore_cannot_be_approved_again(profile, approver):
    chore = ChoreInstance(
        title="Dishes",
        xp_value=10,
        status=ChoreStatus.PENDING,
        assignee=profile,
    )
    chore.mark_pending()
    chore.approve(approver=approver, via=ApprovalSource.PEER)
    chore.save()

    with pytest.raises(ValidationError, match="Only pending chores can be approved"):
        chore.approve(approver=approver, via=ApprovalSource.PEER)
