import pytest

from homework_quest.models import ApprovalSource, ChoreInstance, ChoreStatus, Profile
from homework_quest.services import ApprovalError, peer_approve


def _profile(name, pin):
    profile = Profile(name=name, pin_hash="")
    profile.set_pin(pin)
    profile.save()
    return profile


@pytest.fixture
def assignee(db):
    return _profile("Alex", "1234")


@pytest.fixture
def approver(db):
    return _profile("Blake", "5678")


@pytest.fixture
def pending_chore(db, assignee):
    chore = ChoreInstance(title="Dishes", xp_value=25, assignee=assignee)
    chore.mark_pending()
    chore.save()
    return chore


@pytest.mark.django_db
def test_peer_approve_grants_xp(pending_chore, assignee, approver):
    peer_approve(pending_chore, approver, "5678")

    pending_chore.refresh_from_db()
    assignee.refresh_from_db()
    assert pending_chore.status == ChoreStatus.APPROVED
    assert pending_chore.approver_id == approver.pk
    assert pending_chore.approved_via == ApprovalSource.PEER
    assert assignee.current_cycle_xp == 25


@pytest.mark.django_db
def test_peer_approve_rejects_wrong_pin(pending_chore, assignee, approver):
    with pytest.raises(ApprovalError, match="Invalid PIN"):
        peer_approve(pending_chore, approver, "0000")

    pending_chore.refresh_from_db()
    assignee.refresh_from_db()
    assert pending_chore.status == ChoreStatus.PENDING
    assert assignee.current_cycle_xp == 0


@pytest.mark.django_db
def test_peer_approve_rejects_self_approval(pending_chore, assignee):
    with pytest.raises(ApprovalError, match="Cannot approve your own chore"):
        peer_approve(pending_chore, assignee, "1234")

    pending_chore.refresh_from_db()
    assignee.refresh_from_db()
    assert pending_chore.status == ChoreStatus.PENDING
    assert assignee.current_cycle_xp == 0
