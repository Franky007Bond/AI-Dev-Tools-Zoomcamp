from __future__ import annotations

import copy
from datetime import datetime, timezone
from typing import Any, Callable

from backend.errors import WaitlyError
from backend.forecast import with_wait_estimates
from backend.store import MockStore, summarize_analytics, _iso

WAITING_STATUSES = {"waiting", "notified", "confirmed"}


class WaitlyService:
    def __init__(self, store: MockStore, now_fn: Callable[[], datetime]) -> None:
        self.store = store
        self.now_fn = now_fn

    def _now(self) -> datetime:
        return self.now_fn()

    def _next_id(self, prefix: str) -> str:
        return self.store.next_id(prefix)

    def _require_party(self, party_id: str) -> dict[str, Any]:
        for party in self.store.state["parties"]:
            if party["id"] == party_id:
                return party
        raise WaitlyError(f"Party {party_id} not found", status_code=404, code="party_not_found")

    def _tables_view(self) -> list[dict[str, Any]]:
        tables: list[dict[str, Any]] = []
        for table in self.store.state["tables"]:
            extra = self.store.state["table_state"][table["id"]]
            party = next(
                (item for item in self.store.state["parties"] if item["id"] == extra["partyId"]),
                None,
            )
            tables.append(
                {
                    **table,
                    "status": extra["status"],
                    "partyId": extra["partyId"],
                    "occupiedAt": extra["occupiedAt"],
                    "partyName": party["name"] if party else None,
                }
            )
        return tables

    def _compact_queue(self) -> None:
        waiting = sorted(
            [party for party in self.store.state["parties"] if party["status"] in WAITING_STATUSES],
            key=lambda party: party["position"] or 0,
        )
        for index, party in enumerate(waiting):
            party["position"] = index + 1

    def _activate_due_reservations(self, clock: datetime) -> None:
        clock_ms = clock.timestamp() * 1000
        for party in self.store.state["parties"]:
            if (
                party["source"] == "reservation"
                and party["status"] == "upcoming"
                and party["reservationTime"]
                and datetime.fromisoformat(party["reservationTime"].replace("Z", "+00:00")).timestamp() * 1000
                <= clock_ms
            ):
                last_position = max(
                    (
                        item["position"] or 0
                        for item in self.store.state["parties"]
                        if item["status"] in WAITING_STATUSES
                    ),
                    default=0,
                )
                party["status"] = "waiting"
                party["position"] = last_position + 1
                party["queuedAt"] = party["reservationTime"]

    def _apply_no_shows(self, clock: datetime) -> None:
        grace_ms = self.store.state["settings"]["gracePeriodMinutes"] * 60000
        clock_ms = clock.timestamp() * 1000
        removed = False

        for party in self.store.state["parties"]:
            if party["status"] != "notified" or not party["notifiedAt"]:
                continue
            notified_ms = datetime.fromisoformat(party["notifiedAt"].replace("Z", "+00:00")).timestamp() * 1000
            if clock_ms - notified_ms < grace_ms:
                continue

            party["status"] = "no-show"
            party["position"] = None
            if party["tableId"]:
                table = self.store.state["table_state"].get(party["tableId"])
                if table and table["partyId"] == party["id"]:
                    self.store.state["table_state"][party["tableId"]] = {
                        "status": "free",
                        "partyId": None,
                        "occupiedAt": None,
                    }
            party["tableId"] = None
            self.store.state["events"].append(
                {
                    "id": self._next_id("e"),
                    "type": "no-show",
                    "at": _iso(clock),
                    "waitMinutes": None,
                    "hour": clock.hour,
                }
            )
            self.store.state["sms"].append(
                {
                    "id": self._next_id("s"),
                    "partyId": party["id"],
                    "direction": "outbound",
                    "kind": "noshow",
                    "body": f"Waitly: {party['name']} was removed after the grace period. Reply if this was a mistake.",
                    "at": _iso(clock),
                }
            )
            self.store.state["host_notices"].insert(
                0,
                {
                    "id": self._next_id("n"),
                    "at": _iso(clock),
                    "text": f"{party['name']} was auto-removed as a no-show.",
                },
            )
            removed = True

        if removed:
            self._compact_queue()

    def snapshot(self, clock: datetime | None = None) -> dict[str, Any]:
        clock = clock or self._now()
        self._activate_due_reservations(clock)
        self._apply_no_shows(clock)
        self._compact_queue()
        tables = self._tables_view()
        parties = with_wait_estimates(copy.deepcopy(self.store.state["parties"]), tables, clock)

        return {
            "now": _iso(clock),
            "settings": dict(self.store.state["settings"]),
            "tables": tables,
            "parties": parties,
            "queue": sorted(
                [party for party in parties if party["status"] in WAITING_STATUSES],
                key=lambda party: party["position"] or 0,
            ),
            "upcoming": sorted(
                [party for party in parties if party["status"] == "upcoming"],
                key=lambda party: datetime.fromisoformat(party["reservationTime"].replace("Z", "+00:00")),
            ),
            "sms": sorted(
                copy.deepcopy(self.store.state["sms"]),
                key=lambda message: datetime.fromisoformat(message["at"].replace("Z", "+00:00")),
                reverse=True,
            ),
            "hostNotices": copy.deepcopy(self.store.state["host_notices"])[:8],
        }

    def _add_sms(
        self,
        party: dict[str, Any],
        kind: str,
        body: str,
        clock: datetime,
        direction: str = "outbound",
    ) -> None:
        self.store.state["sms"].append(
            {
                "id": self._next_id("s"),
                "partyId": party["id"],
                "direction": direction,
                "kind": kind,
                "body": body,
                "at": _iso(clock),
            }
        )

    def add_party(self, input_data: dict[str, Any], clock: datetime | None = None) -> dict[str, Any]:
        clock = clock or self._now()
        source = input_data.get("source", "walk-in")
        reservation_time = input_data.get("reservationTime")
        is_future_reservation = (
            source == "reservation"
            and reservation_time
            and datetime.fromisoformat(reservation_time.replace("Z", "+00:00")).timestamp() * 1000
            > clock.timestamp() * 1000
        )

        party: dict[str, Any] = {
            "id": self._next_id("p"),
            "name": input_data["name"].strip(),
            "phone": input_data["phone"].strip(),
            "partySize": int(input_data["partySize"]),
            "notes": (input_data.get("notes") or "").strip(),
            "source": source,
            "status": "upcoming" if is_future_reservation else "waiting",
            "position": None,
            "queuedAt": _iso(clock),
            "reservationTime": reservation_time,
            "tableId": input_data.get("tableId"),
            "notifiedAt": None,
        }

        if not is_future_reservation:
            last_position = max(
                (
                    item["position"] or 0
                    for item in self.store.state["parties"]
                    if item["status"] in WAITING_STATUSES
                ),
                default=0,
            )
            party["position"] = last_position + 1

        if party["tableId"]:
            table = self.store.state["table_state"].get(party["tableId"])
            if not table or table["status"] != "free":
                raise WaitlyError(
                    "Reservation table is not free",
                    status_code=409,
                    code="table_not_free",
                )
            self.store.state["table_state"][party["tableId"]] = {
                "status": "reserved",
                "partyId": party["id"],
                "occupiedAt": None,
            }

        self.store.state["parties"].append(party)
        preview = self.snapshot(clock)
        created = next(item for item in preview["parties"] if item["id"] == party["id"])
        wait = created.get("waitEstimateMinutes")
        if source == "reservation":
            body = f"Waitly: Reservation for {party['name']} party of {party['partySize']}"
            if party["tableId"]:
                body += " is holding a table"
            body += "."
        else:
            body = f"Waitly: {party['name']} party of {party['partySize']} is on the list."
            if wait:
                body += f" Estimated wait {wait} min."
        self._add_sms(party, "join", body, clock)
        snap = self.snapshot(clock)
        return snap, party["id"]

    def add_party_snapshot(self, input_data: dict[str, Any], clock: datetime | None = None) -> dict[str, Any]:
        snap, _party_id = self.add_party(input_data, clock)
        return snap

    def join_waitlist(self, input_data: dict[str, Any], clock: datetime | None = None) -> dict[str, Any]:
        clock = clock or self._now()
        payload = {**input_data, "source": "remote"}
        snap, party_id = self.add_party(payload, clock)
        return next(party for party in snap["parties"] if party["id"] == party_id)

    def update_party(
        self,
        party_id: str,
        patch: dict[str, Any],
        clock: datetime | None = None,
    ) -> dict[str, Any]:
        clock = clock or self._now()
        party = self._require_party(party_id)
        if patch.get("name") is not None:
            party["name"] = patch["name"].strip()
        if patch.get("phone") is not None:
            party["phone"] = patch["phone"].strip()
        if patch.get("partySize") is not None:
            party["partySize"] = int(patch["partySize"])
        if patch.get("notes") is not None:
            party["notes"] = patch["notes"].strip()
        if "reservationTime" in patch:
            party["reservationTime"] = patch["reservationTime"]
        return self.snapshot(clock)

    def remove_party(self, party_id: str, clock: datetime | None = None) -> dict[str, Any]:
        clock = clock or self._now()
        party = self._require_party(party_id)
        party["status"] = "cancelled"
        party["position"] = None
        if party["tableId"]:
            table = self.store.state["table_state"].get(party["tableId"])
            if table and table["partyId"] == party["id"]:
                self.store.state["table_state"][party["tableId"]] = {
                    "status": "free",
                    "partyId": None,
                    "occupiedAt": None,
                }
        party["tableId"] = None
        self._add_sms(party, "cancel", f"Waitly: {party['name']} was removed from the waitlist.", clock)
        return self.snapshot(clock)

    def reorder_queue(
        self,
        from_position: int,
        to_position: int,
        clock: datetime | None = None,
    ) -> dict[str, Any]:
        clock = clock or self._now()
        queue = sorted(
            [party for party in self.store.state["parties"] if party["status"] in WAITING_STATUSES],
            key=lambda party: party["position"] or 0,
        )
        from_index = from_position - 1
        to_index = to_position - 1
        if (
            from_index < 0
            or to_index < 0
            or from_index >= len(queue)
            or to_index >= len(queue)
        ):
            raise WaitlyError("Invalid queue position", status_code=422, code="invalid_position")
        moved = queue.pop(from_index)
        queue.insert(to_index, moved)
        for index, party in enumerate(queue):
            party["position"] = index + 1
        return self.snapshot(clock)

    def notify_ready(self, party_id: str, clock: datetime | None = None) -> dict[str, Any]:
        clock = clock or self._now()
        party = self._require_party(party_id)
        if party["status"] not in WAITING_STATUSES:
            raise WaitlyError("Party is not waiting", status_code=409, code="party_not_waiting")
        party["status"] = "notified"
        party["notifiedAt"] = _iso(clock)
        self._add_sms(
            party,
            "ready",
            f"Waitly: {party['name']}, your table is ready. Reply YES to confirm or CANCEL to drop off.",
            clock,
        )
        self.store.state["host_notices"].insert(
            0,
            {
                "id": self._next_id("n"),
                "at": _iso(clock),
                "text": f"{party['name']} was texted that their table is ready.",
            },
        )
        return self.snapshot(clock)

    def sms_reply(
        self,
        party_id: str,
        reply: str,
        clock: datetime | None = None,
    ) -> dict[str, Any]:
        clock = clock or self._now()
        party = self._require_party(party_id)
        normalized = reply.strip().lower()
        if normalized in {"yes", "confirm"}:
            party["status"] = "confirmed"
            self._add_sms(party, "confirm", "YES", clock, direction="inbound")
            self._add_sms(party, "confirm", f"Waitly: Thanks {party['name']}, see you shortly.", clock)
            return self.snapshot(clock)
        if normalized == "cancel":
            self._add_sms(party, "cancel", "CANCEL", clock, direction="inbound")
            return self.remove_party(party_id, clock)
        raise WaitlyError("Reply must be YES or CANCEL", status_code=422, code="invalid_reply")

    def seat_party(
        self,
        party_id: str,
        table_id: str,
        clock: datetime | None = None,
    ) -> dict[str, Any]:
        clock = clock or self._now()
        party = self._require_party(party_id)
        table = self.store.state["table_state"].get(table_id)
        if not table:
            raise WaitlyError("Table not found", status_code=404, code="table_not_found")
        if table["status"] == "occupied":
            raise WaitlyError("Table is occupied", status_code=409, code="table_occupied")
        if table["status"] == "reserved" and table["partyId"] != party_id:
            raise WaitlyError(
                "Table is reserved for another party",
                status_code=409,
                code="table_reserved",
            )

        if party["tableId"] and party["tableId"] != table_id:
            previous = self.store.state["table_state"].get(party["tableId"])
            if previous and previous["partyId"] == party_id:
                self.store.state["table_state"][party["tableId"]] = {
                    "status": "free",
                    "partyId": None,
                    "occupiedAt": None,
                }

        queued_at = datetime.fromisoformat(party["queuedAt"].replace("Z", "+00:00"))
        wait_minutes = max(0, round((clock - queued_at).total_seconds() / 60))
        party["status"] = "seated"
        party["position"] = None
        party["tableId"] = table_id
        party["seatedAt"] = _iso(clock)
        party["seatedWaitMinutes"] = wait_minutes
        self.store.state["table_state"][table_id] = {
            "status": "occupied",
            "partyId": party_id,
            "occupiedAt": _iso(clock),
        }
        self.store.state["events"].append(
            {
                "id": self._next_id("e"),
                "type": "seated",
                "at": _iso(clock),
                "waitMinutes": wait_minutes,
                "hour": clock.hour,
            }
        )
        table_name = next(item["name"] for item in self.store.state["tables"] if item["id"] == table_id)
        self._add_sms(
            party,
            "seated",
            f"Waitly: {party['name']} is seated at {table_name}.",
            clock,
        )
        return self.snapshot(clock)

    def set_table_status(
        self,
        table_id: str,
        status: str,
        clock: datetime | None = None,
    ) -> dict[str, Any]:
        clock = clock or self._now()
        table = self.store.state["table_state"].get(table_id)
        if not table:
            raise WaitlyError("Table not found", status_code=404, code="table_not_found")

        if status == "occupied":
            self.store.state["table_state"][table_id] = {
                "status": "occupied",
                "partyId": table["partyId"],
                "occupiedAt": table["occupiedAt"] or _iso(clock),
            }
            return self.snapshot(clock)

        if status == "free":
            previous_party_id = table["partyId"]
            self.store.state["table_state"][table_id] = {
                "status": "free",
                "partyId": None,
                "occupiedAt": None,
            }
            reserved_party = next(
                (
                    party
                    for party in self.store.state["parties"]
                    if party["id"] == previous_party_id
                    and party["source"] == "reservation"
                    and party["status"] in WAITING_STATUSES
                ),
                None,
            )
            if reserved_party:
                reserved_party["tableId"] = None

            freed = self.snapshot(clock)
            table_view = next(item for item in freed["tables"] if item["id"] == table_id)
            table_def = next(item for item in self.store.state["tables"] if item["id"] == table_id)
            next_party = next(
                (
                    party
                    for party in freed["queue"]
                    if party["status"] == "waiting"
                    and party["partySize"] <= table_def["seats"]
                    and (not party["tableId"] or party["tableId"] == table_id)
                ),
                None,
            )
            if next_party and table_view["status"] == "free":
                return self.notify_ready(next_party["id"], clock)
            return freed

        if status == "reserved":
            self.store.state["table_state"][table_id] = {
                "status": "reserved",
                "partyId": table["partyId"],
                "occupiedAt": None,
            }
            return self.snapshot(clock)

        raise WaitlyError("Unknown table status", status_code=422, code="invalid_status")

    def receive_sms(
        self,
        phone: str,
        body: str,
        clock: datetime | None = None,
    ) -> tuple[dict[str, Any], str | None]:
        clock = clock or self._now()
        party = next(
            (item for item in self.store.state["parties"] if item["phone"] == phone),
            None,
        )
        if not party:
            raise WaitlyError(f"No party found for {phone}", status_code=404, code="party_not_found")
        snap = self.sms_reply(party["id"], body, clock)
        return snap, party["id"]

    def get_analytics(self, range_name: str = "daily", clock: datetime | None = None) -> dict[str, Any]:
        clock = clock or self._now()
        self.snapshot(clock)
        return summarize_analytics(self.store.state["events"], range_name=range_name, now=clock)

    def update_settings(self, patch: dict[str, Any], clock: datetime | None = None) -> dict[str, Any]:
        clock = clock or self._now()
        self.store.state["settings"] = {**self.store.state["settings"], **patch}
        return self.snapshot(clock)

    def reset_demo(self, clock: datetime | None = None) -> dict[str, Any]:
        clock = clock or self._now()
        self.store.reset(clock)
        return self.snapshot(clock)
