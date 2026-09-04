import pytest

from homework_quest.models import ChoreInstance, ChoreStatus, ChoreTemplate, Profile
from homework_quest.services import (
    ApprovalError,
    claim_open_bounty_with_pin,
    log_chore_with_pin,
    log_template_chore_with_pin,
    resolve_profile_by_pin,
)


def _profile(name, pin):
    profile = Profile(name=name, pin_hash="")
    profile.set_pin(pin)
    profile.save()
    return profile


@pytest.mark.django_db
def test_resolve_profile_by_pin():
    alex = _profile("Alex", "1234")
    assert resolve_profile_by_pin("1234").pk == alex.pk


@pytest.mark.django_db
def test_resolve_profile_rejects_invalid_pin():
    _profile("Alex", "1234")
    with pytest.raises(ApprovalError):
        resolve_profile_by_pin("0000")


@pytest.mark.django_db
def test_log_chore_with_pin_creates_pending_instance():
    _profile("Alex", "1234")
    chore = log_chore_with_pin(pin="1234", title="Dishes", xp_value=30)
    assert chore.status == ChoreStatus.PENDING
    assert chore.assignee.name == "Alex"
    assert chore.submitted_at is not None
    assert chore.auto_approve_at is not None


@pytest.mark.django_db
def test_log_template_chore_with_pin():
    _profile("Alex", "1234")
    template = ChoreTemplate.objects.create(
        title="Vacuum",
        category="Cleaning",
        estimated_minutes=30,
    )
    chore = log_template_chore_with_pin(pin="1234", template=template)
    assert chore.template_id == template.pk
    assert chore.status == ChoreStatus.PENDING


@pytest.mark.django_db
def test_claim_open_bounty_with_pin():
    alex = _profile("Alex", "1234")
    bounty = ChoreInstance.objects.create(
        title="Garage",
        xp_value=55,
        status=ChoreStatus.OPEN,
    )
    claimed = claim_open_bounty_with_pin(pin="1234", chore=bounty)
    assert claimed.pk == bounty.pk
    assert claimed.assignee_id == alex.pk
    assert claimed.status == ChoreStatus.PENDING
