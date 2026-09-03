"""Pending review queue context."""

from datetime import timedelta

from django.utils import timezone

from homework_quest.models import ChoreInstance, ChoreStatus

AUTO_APPROVE_WINDOW = timedelta(hours=24)
NEARING_AUTO_APPROVE_THRESHOLD = timedelta(hours=18)


def _timeout_progress(chore: ChoreInstance, *, now) -> tuple[int, bool]:
    if not chore.submitted_at or not chore.auto_approve_at:
        return 0, False

    window = chore.auto_approve_at - chore.submitted_at
    if window.total_seconds() <= 0:
        return 100, True

    elapsed = now - chore.submitted_at
    progress = int(min(100, max(0, elapsed / window * 100)))
    nearing = elapsed >= NEARING_AUTO_APPROVE_THRESHOLD
    return progress, nearing


def build_review_queue_context() -> dict:
    now = timezone.now()
    pending = (
        ChoreInstance.objects.filter(status=ChoreStatus.PENDING)
        .select_related("assignee")
        .order_by("submitted_at")
    )

    queue_items = []
    for chore in pending:
        progress, nearing_auto = _timeout_progress(chore, now=now)
        assignee = chore.assignee
        queue_items.append(
            {
                "chore": chore,
                "assignee": assignee,
                "assignee_name": assignee.name if assignee else "Unknown",
                "timeout_progress": progress,
                "nearing_auto_approve": nearing_auto,
            }
        )

    return {
        "queue_items": queue_items,
        "auto_approve_hours": int(AUTO_APPROVE_WINDOW.total_seconds() // 3600),
    }
