"""Chore pool page context."""

from homework_quest.models import ChoreInstance, ChoreStatus, ChoreTemplate
from homework_quest.xp import xp_from_minutes


def build_chore_pool_context(*, active_tab: str = "routines") -> dict:
    routines = ChoreTemplate.objects.order_by("title")
    bounties = ChoreInstance.objects.filter(status=ChoreStatus.OPEN).order_by("-id")
    return {
        "active_tab": active_tab,
        "routines": routines,
        "bounties": bounties,
        "default_effort_xp": xp_from_minutes(5),
    }
