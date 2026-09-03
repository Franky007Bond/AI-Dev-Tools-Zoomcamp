"""Dashboard context for the kitchen idle screen."""

from django.utils import timezone

from homework_quest.cycle import get_open_cycle
from homework_quest.models import ApprovalSource, ChoreInstance, ChoreStatus, Profile


def feed_status_label(chore: ChoreInstance) -> str:
    if chore.status == ChoreStatus.PENDING:
        return "Pending Approval"
    if chore.status == ChoreStatus.APPROVED:
        if chore.approved_via == ApprovalSource.AUTO:
            return "Auto-Approved"
        return "Verified"
    return chore.status


def build_dashboard_context() -> dict:
    profiles = list(Profile.objects.order_by("-current_cycle_xp", "name"))
    leader_xp = profiles[0].current_cycle_xp if profiles else 0

    standings = []
    for profile in profiles:
        if leader_xp:
            progress = int(profile.current_cycle_xp / leader_xp * 100)
        else:
            progress = 0
        standings.append(
            {
                "profile": profile,
                "xp": profile.current_cycle_xp,
                "progress_vs_leader": progress,
            }
        )

    cycle = get_open_cycle()
    stake = cycle.selected_perk if cycle else None
    reset_at = cycle.end_time if cycle else None

    if reset_at:
        remaining = reset_at - timezone.now()
        if remaining.total_seconds() <= 0:
            countdown = "Reset due"
        else:
            days = remaining.days
            hours = remaining.seconds // 3600
            countdown = f"{days}d {hours}h until reset"
    else:
        countdown = "No active cycle"

    feed_qs = (
        ChoreInstance.objects.filter(
            status__in=[ChoreStatus.PENDING, ChoreStatus.APPROVED],
            submitted_at__isnull=False,
        )
        .select_related("assignee", "approver")
        .order_by("-submitted_at")[:50]
    )
    feed_items = [
        {
            "chore": chore,
            "status_label": feed_status_label(chore),
            "assignee_name": chore.assignee.name if chore.assignee else "Unknown",
        }
        for chore in feed_qs
    ]

    return {
        "standings": standings,
        "leader_xp": leader_xp,
        "stake": stake,
        "cycle": cycle,
        "countdown": countdown,
        "feed_items": feed_items,
    }
