from __future__ import annotations

from datetime import datetime
from typing import Any

AVERAGE_DINING_MINUTES = 45
MINUTES_PER_PARTY_AHEAD = 10
SEAT_NOW_MINUTES = 5


def estimate_wait_minutes(
    *,
    party_size: int,
    queue_ahead: list[dict[str, Any]],
    tables: list[dict[str, Any]],
    now: datetime,
) -> int:
    fitting = [table for table in tables if table["seats"] >= party_size]
    if not fitting:
        return 90

    free = [table for table in fitting if table["status"] == "free"]
    occupied = [table for table in fitting if table["status"] == "occupied"]
    ahead = len(queue_ahead)

    if len(free) > ahead:
        return SEAT_NOW_MINUTES * (ahead + 1)

    now_ms = now.timestamp() * 1000
    remaining_turnover: list[float] = []
    for table in occupied:
        occupied_at = table.get("occupiedAt")
        if occupied_at:
            occupied_ms = datetime.fromisoformat(occupied_at.replace("Z", "+00:00")).timestamp() * 1000
        else:
            occupied_ms = now_ms
        elapsed_minutes = max(0, (now_ms - occupied_ms) / 60000)
        remaining_turnover.append(max(5, AVERAGE_DINING_MINUTES - elapsed_minutes))

    next_table_minutes = min(remaining_turnover) if remaining_turnover else AVERAGE_DINING_MINUTES
    return round(
        next_table_minutes + MINUTES_PER_PARTY_AHEAD * max(0, ahead - len(free))
    )


def with_wait_estimates(
    parties: list[dict[str, Any]],
    tables: list[dict[str, Any]],
    now: datetime,
) -> list[dict[str, Any]]:
    waiting_statuses = {"waiting", "notified", "confirmed"}
    waiting = [party for party in parties if party["status"] in waiting_statuses]

    result: list[dict[str, Any]] = []
    for party in parties:
        if party["status"] not in waiting_statuses:
            result.append({**party, "waitEstimateMinutes": None})
            continue

        queue_ahead = [
            other
            for other in waiting
            if other["position"] is not None
            and party["position"] is not None
            and other["position"] < party["position"]
        ]
        result.append(
            {
                **party,
                "waitEstimateMinutes": estimate_wait_minutes(
                    party_size=party["partySize"],
                    queue_ahead=queue_ahead,
                    tables=tables,
                    now=now,
                ),
            }
        )
    return result
