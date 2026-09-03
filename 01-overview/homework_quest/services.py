from django.utils import timezone

from homework_quest.models import ApprovalSource, ChoreInstance, ChoreStatus, Profile


class ApprovalError(Exception):
    pass


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
