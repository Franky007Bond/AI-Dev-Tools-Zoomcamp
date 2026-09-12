from __future__ import annotations

import copy
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _hour_label(hour: int) -> str:
    suffix = "pm" if hour >= 12 else "am"
    normalized = hour % 12 or 12
    return f"{normalized}{suffix}"


def create_seed_state(now: datetime | None = None) -> dict[str, Any]:
    clock = now or datetime.now(timezone.utc)
    now_ms = clock.timestamp() * 1000

    def ago_minutes(minutes: float) -> str:
        return _iso(datetime.fromtimestamp((now_ms - minutes * 60000) / 1000, tz=timezone.utc))

    def ago_hours(hours: float) -> str:
        return _iso(datetime.fromtimestamp((now_ms - hours * 3600000) / 1000, tz=timezone.utc))

    tables = [
        {"id": "t1", "name": "T1", "seats": 2, "x": 8, "y": 12, "w": 16, "h": 18},
        {"id": "t2", "name": "T2", "seats": 2, "x": 8, "y": 42, "w": 16, "h": 18},
        {"id": "t3", "name": "T3", "seats": 4, "x": 30, "y": 12, "w": 18, "h": 22},
        {"id": "t4", "name": "T4", "seats": 4, "x": 30, "y": 48, "w": 18, "h": 22},
        {"id": "t5", "name": "T5", "seats": 4, "x": 54, "y": 12, "w": 18, "h": 22},
        {"id": "t6", "name": "T6", "seats": 6, "x": 54, "y": 48, "w": 22, "h": 26},
        {"id": "t7", "name": "T7", "seats": 2, "x": 80, "y": 12, "w": 16, "h": 18},
        {"id": "t8", "name": "T8", "seats": 8, "x": 78, "y": 46, "w": 18, "h": 32},
    ]

    parties = [
        {
            "id": "p1",
            "name": "Nguyen",
            "phone": "555-0101",
            "partySize": 2,
            "notes": "Window if possible",
            "source": "walk-in",
            "status": "waiting",
            "position": 1,
            "queuedAt": ago_minutes(18),
            "reservationTime": None,
            "tableId": None,
            "notifiedAt": None,
        },
        {
            "id": "p2",
            "name": "Patel",
            "phone": "555-0102",
            "partySize": 4,
            "notes": "",
            "source": "remote",
            "status": "waiting",
            "position": 2,
            "queuedAt": ago_minutes(11),
            "reservationTime": None,
            "tableId": None,
            "notifiedAt": None,
        },
        {
            "id": "p3",
            "name": "Garcia",
            "phone": "555-0103",
            "partySize": 6,
            "notes": "Birthday",
            "source": "walk-in",
            "status": "notified",
            "position": 3,
            "queuedAt": ago_minutes(28),
            "reservationTime": None,
            "tableId": None,
            "notifiedAt": ago_minutes(2),
        },
        {
            "id": "p4",
            "name": "Okoye",
            "phone": "555-0104",
            "partySize": 4,
            "notes": "Anniversary",
            "source": "reservation",
            "status": "waiting",
            "position": 4,
            "queuedAt": ago_minutes(5),
            "reservationTime": ago_minutes(5),
            "tableId": "t5",
            "notifiedAt": None,
        },
        {
            "id": "p5",
            "name": "Berg",
            "phone": "555-0105",
            "partySize": 2,
            "notes": "",
            "source": "walk-in",
            "status": "seated",
            "position": None,
            "queuedAt": ago_minutes(50),
            "reservationTime": None,
            "tableId": "t1",
            "notifiedAt": None,
            "seatedAt": ago_minutes(22),
            "seatedWaitMinutes": 28,
        },
        {
            "id": "p6",
            "name": "Chen",
            "phone": "555-0106",
            "partySize": 4,
            "notes": "",
            "source": "walk-in",
            "status": "seated",
            "position": None,
            "queuedAt": ago_minutes(70),
            "reservationTime": None,
            "tableId": "t4",
            "notifiedAt": None,
            "seatedAt": ago_minutes(40),
            "seatedWaitMinutes": 30,
        },
    ]

    table_state = {
        "t1": {"status": "occupied", "partyId": "p5", "occupiedAt": ago_minutes(22)},
        "t2": {"status": "free", "partyId": None, "occupiedAt": None},
        "t3": {"status": "free", "partyId": None, "occupiedAt": None},
        "t4": {"status": "occupied", "partyId": "p6", "occupiedAt": ago_minutes(40)},
        "t5": {"status": "reserved", "partyId": "p4", "occupiedAt": None},
        "t6": {"status": "free", "partyId": None, "occupiedAt": None},
        "t7": {"status": "free", "partyId": None, "occupiedAt": None},
        "t8": {"status": "free", "partyId": None, "occupiedAt": None},
    }

    sms = [
        {
            "id": "s1",
            "partyId": "p1",
            "direction": "outbound",
            "kind": "join",
            "body": "Waitly: Nguyen party of 2 is on the list. Estimated wait 10 min.",
            "at": ago_minutes(18),
        },
        {
            "id": "s2",
            "partyId": "p2",
            "direction": "outbound",
            "kind": "join",
            "body": "Waitly: Patel party of 4 is on the list. Estimated wait 20 min.",
            "at": ago_minutes(11),
        },
        {
            "id": "s3",
            "partyId": "p3",
            "direction": "outbound",
            "kind": "join",
            "body": "Waitly: Garcia party of 6 is on the list. Estimated wait 25 min.",
            "at": ago_minutes(28),
        },
        {
            "id": "s4",
            "partyId": "p3",
            "direction": "outbound",
            "kind": "ready",
            "body": "Waitly: Garcia, your table is ready. Reply YES to confirm or CANCEL to drop off.",
            "at": ago_minutes(2),
        },
        {
            "id": "s5",
            "partyId": "p4",
            "direction": "outbound",
            "kind": "join",
            "body": "Waitly: Reservation for Okoye party of 4 is holding T5.",
            "at": ago_minutes(5),
        },
    ]

    events = [
        {"id": "e1", "type": "seated", "at": ago_hours(3), "waitMinutes": 12, "hour": datetime.fromisoformat(ago_hours(3).replace("Z", "+00:00")).hour},
        {"id": "e2", "type": "seated", "at": ago_hours(2), "waitMinutes": 22, "hour": datetime.fromisoformat(ago_hours(2).replace("Z", "+00:00")).hour},
        {"id": "e3", "type": "no-show", "at": ago_minutes(90), "waitMinutes": None, "hour": datetime.fromisoformat(ago_minutes(90).replace("Z", "+00:00")).hour},
        {"id": "e4", "type": "seated", "at": ago_minutes(40), "waitMinutes": 30, "hour": datetime.fromisoformat(ago_minutes(40).replace("Z", "+00:00")).hour},
        {"id": "e5", "type": "seated", "at": ago_minutes(22), "waitMinutes": 28, "hour": datetime.fromisoformat(ago_minutes(22).replace("Z", "+00:00")).hour},
        {"id": "e6", "type": "seated", "at": ago_hours(26), "waitMinutes": 18, "hour": datetime.fromisoformat(ago_hours(26).replace("Z", "+00:00")).hour},
    ]

    return {
        "next_id": 20,
        "settings": {
            "restaurantName": "Waitly Bistro",
            "gracePeriodMinutes": 8,
        },
        "tables": tables,
        "table_state": table_state,
        "parties": parties,
        "sms": sms,
        "events": events,
        "host_notices": [
            {
                "id": "n1",
                "at": ago_minutes(2),
                "text": "Garcia was texted that their table is ready.",
            }
        ],
    }


@dataclass
class MockStore:
    """In-memory mock database; replace with a real DB later."""

    state: dict[str, Any]
    seq: int = 20
    next_id_fn: Callable[[str], str] | None = None

    @classmethod
    def create_seed(cls, now: datetime | None = None) -> MockStore:
        seed = create_seed_state(now)
        return cls(state=copy.deepcopy(seed), seq=seed["next_id"])

    def next_id(self, prefix: str) -> str:
        self.seq += 1
        return f"{prefix}{self.seq}"

    def reset(self, now: datetime) -> None:
        seed = create_seed_state(now)
        self.state = copy.deepcopy(seed)
        self.seq = seed["next_id"]


def start_of_day(timestamp: datetime) -> datetime:
    return timestamp.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)


def summarize_analytics(
    events: list[dict[str, Any]],
    *,
    range_name: str = "daily",
    now: datetime,
) -> dict[str, Any]:
    now_ms = now.timestamp() * 1000
    start_ms = (
        now_ms - 7 * 24 * 3600000
        if range_name == "weekly"
        else start_of_day(now).timestamp() * 1000
    )

    in_range = [
        event
        for event in events
        if start_ms <= datetime.fromisoformat(event["at"].replace("Z", "+00:00")).timestamp() * 1000 <= now_ms
    ]

    seated = [event for event in in_range if event["type"] == "seated"]
    noshows = [event for event in in_range if event["type"] == "no-show"]
    avg_wait = (
        sum(event["waitMinutes"] for event in seated) / len(seated) if seated else 0
    )
    outcome_count = len(seated) + len(noshows)

    hours = [{"hour": hour, "label": _hour_label(hour), "count": 0} for hour in range(24)]
    for event in in_range:
        hour = datetime.fromisoformat(event["at"].replace("Z", "+00:00")).hour
        hours[hour]["count"] += 1

    day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    days = [{"weekday": idx, "label": label, "count": 0} for idx, label in enumerate(day_names)]
    for event in in_range:
        weekday = datetime.fromisoformat(event["at"].replace("Z", "+00:00")).weekday()
        # JS getDay(): 0=Sunday; Python weekday(): 0=Monday
        js_weekday = (weekday + 1) % 7
        days[js_weekday]["count"] += 1

    return {
        "range": range_name,
        "averageWaitMinutes": round(avg_wait),
        "partiesSeated": len(seated),
        "noShowRate": 0 if outcome_count == 0 else len(noshows) / outcome_count,
        "busiestHours": [
            row for row in hours if row["count"] > 0 or (11 <= row["hour"] <= 21)
        ],
        "busiestDays": days,
    }
