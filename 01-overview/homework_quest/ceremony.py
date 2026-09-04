"""Weekly ceremony screen context."""

from homework_quest.cycle import get_open_cycle
from homework_quest.models import Perk, Profile, WeeklyCycle


def get_last_closed_cycle() -> WeeklyCycle | None:
    return WeeklyCycle.objects.exclude(winner_ids=[]).order_by("-end_time").first()


def _standings_from_profiles() -> list[dict]:
    rows = []
    for profile in Profile.objects.order_by("-current_cycle_xp", "name"):
        rows.append(
            {
                "profile": profile,
                "name": profile.name,
                "xp": profile.current_cycle_xp,
                "is_winner": False,
            }
        )
    return rows


def _standings_from_closed_cycle(cycle: WeeklyCycle) -> list[dict]:
    winner_ids = {int(wid) for wid in cycle.winner_ids}
    standings = cycle.standings_json or {}
    rows = []
    for profile in Profile.objects.order_by("name"):
        xp = standings.get(str(profile.pk), standings.get(profile.pk, 0))
        rows.append(
            {
                "profile": profile,
                "name": profile.name,
                "xp": xp,
                "is_winner": profile.pk in winner_ids,
            }
        )
    rows.sort(key=lambda row: (-row["xp"], row["name"]))
    return rows


def build_ceremony_context(*, celebrating: bool = False) -> dict:
    open_cycle = get_open_cycle()
    closed_cycle = get_last_closed_cycle() if celebrating else None
    active_perks = list(Perk.objects.filter(is_active=True).order_by("title"))

    if celebrating and closed_cycle:
        standings = _standings_from_closed_cycle(closed_cycle)
        winners = [row for row in standings if row["is_winner"]]
        revealed_perk = open_cycle.selected_perk if open_cycle else None
    else:
        standings = _standings_from_profiles()
        winners = []
        top_xp = standings[0]["xp"] if standings else 0
        if top_xp > 0:
            winners = [row for row in standings if row["xp"] == top_xp]
        revealed_perk = open_cycle.selected_perk if open_cycle else None

    return {
        "celebrating": celebrating,
        "open_cycle": open_cycle,
        "closed_cycle": closed_cycle,
        "standings": standings,
        "winners": winners,
        "revealed_perk": revealed_perk,
        "active_perks": active_perks,
        "shared_victory": len(winners) > 1,
    }
