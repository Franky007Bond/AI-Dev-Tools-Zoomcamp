from django.utils import timezone

from homework_quest.models import (
    ApprovalSource,
    ChoreInstance,
    ChoreStatus,
    ChoreTemplate,
    Profile,
)
from homework_quest.xp import xp_from_minutes


class ApprovalError(Exception):
    pass


def resolve_profile_by_pin(pin: str) -> Profile:
    """Return the household member matching a 4-digit PIN."""
    for profile in Profile.objects.all():
        if profile.check_pin(pin):
            return profile
    raise ApprovalError("Invalid PIN.")


def log_chore_with_pin(
    *,
    pin: str,
    title: str,
    xp_value: int,
    template: ChoreTemplate | None = None,
) -> ChoreInstance:
    """Identify the member by PIN, then create a pending chore instance."""
    assignee = resolve_profile_by_pin(pin)
    chore = ChoreInstance(
        title=title,
        xp_value=xp_value,
        assignee=assignee,
        template=template,
    )
    chore.mark_pending()
    chore.save()
    return chore


def log_template_chore_with_pin(*, pin: str, template: ChoreTemplate) -> ChoreInstance:
    return log_chore_with_pin(
        pin=pin,
        title=template.title,
        xp_value=template.base_xp,
        template=template,
    )


def claim_open_bounty_with_pin(*, pin: str, chore: ChoreInstance) -> ChoreInstance:
    """Claim an open ad-hoc bounty and submit it as pending for the PIN holder."""
    if chore.status != ChoreStatus.OPEN:
        raise ApprovalError("Only open bounties can be logged.")
    assignee = resolve_profile_by_pin(pin)
    chore.assignee = assignee
    chore.mark_pending()
    chore.save()
    return chore


def create_adhoc_bounty(*, title: str, _category: str = "", estimated_minutes: int) -> ChoreInstance:
    """Post an unassigned ad-hoc bounty to the board."""
    if not title.strip():
        raise ApprovalError("Title is required.")
    if estimated_minutes <= 0:
        raise ApprovalError("Estimated minutes must be positive.")
    return ChoreInstance.objects.create(
        title=title.strip(),
        xp_value=xp_from_minutes(estimated_minutes),
        status=ChoreStatus.OPEN,
    )


def log_chore(assignee: Profile, pin: str, title: str, xp_value: int) -> ChoreInstance:
    if not assignee.check_pin(pin):
        raise ApprovalError("Invalid PIN.")
    chore = ChoreInstance(title=title, xp_value=xp_value, assignee=assignee)
    chore.mark_pending()
    chore.save()
    return chore


def peer_approve(chore: ChoreInstance, approver: Profile, pin: str) -> None:
    if chore.status != ChoreStatus.PENDING:
        raise ApprovalError("Only pending chores can be approved.")
    if chore.assignee_id == approver.pk:
        raise ApprovalError("Cannot approve your own chore.")
    if not approver.check_pin(pin):
        raise ApprovalError("Invalid PIN.")

    chore.approve(approver=approver, via=ApprovalSource.PEER)
    chore.save()

    assignee = chore.assignee
    assignee.current_cycle_xp += chore.xp_value
    assignee.save(update_fields=["current_cycle_xp"])


def auto_approve_due_chores(now=None) -> int:
    """Approve pending chores past auto_approve_at and grant XP. Returns count approved."""
    now = now or timezone.now()
    due_chores = ChoreInstance.objects.filter(
        status=ChoreStatus.PENDING,
        auto_approve_at__lte=now,
    )
    approved_count = 0
    for chore in due_chores:
        chore.approve(approver=None, via=ApprovalSource.AUTO)
        chore.save()

        assignee = chore.assignee
        assignee.current_cycle_xp += chore.xp_value
        assignee.save(update_fields=["current_cycle_xp"])
        approved_count += 1
    return approved_count
