from datetime import timedelta

import pytest
from django.utils import timezone

from homework_quest.models import ApprovalSource, ChoreInstance, ChoreStatus, Profile
from homework_quest.services import auto_approve_due_chores


def _profile(name):
    profile = Profile(name=name, pin_hash="")
    profile.set_pin("1234")
    profile.save()
    return profile


def _pending_chore(assignee, *, submitted_at):
    chore = ChoreInstance(title="Laundry", xp_value=40, assignee=assignee)
    chore.mark_pending(submitted_at=submitted_at)
    chore.save()
    return chore


@pytest.mark.django_db
def test_auto_approve_only_due_chores():
    assignee = _profile("Alex")
    now = timezone.now()

    due = _pending_chore(assignee, submitted_at=now - timedelta(hours=25))
    future = _pending_chore(assignee, submitted_at=now - timedelta(hours=1))

    approved_count = auto_approve_due_chores(now=now)

    due.refresh_from_db()
    future.refresh_from_db()
    assignee.refresh_from_db()

    assert approved_count == 1
    assert due.status == ChoreStatus.APPROVED
    assert due.approved_via == ApprovalSource.AUTO
    assert due.approver_id is None
    assert assignee.current_cycle_xp == 40
    assert future.status == ChoreStatus.PENDING
    assert future.approved_via == ""


@pytest.mark.django_db
def test_auto_approve_is_idempotent():
    assignee = _profile("Alex")
    now = timezone.now()
    chore = _pending_chore(assignee, submitted_at=now - timedelta(hours=30))

    first_count = auto_approve_due_chores(now=now)
    second_count = auto_approve_due_chores(now=now)

    assignee.refresh_from_db()
    assert first_count == 1
    assert second_count == 0
    assert assignee.current_cycle_xp == 40
