from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PartySource(str, Enum):
    walk_in = "walk-in"
    remote = "remote"
    reservation = "reservation"


class PartyStatus(str, Enum):
    waiting = "waiting"
    notified = "notified"
    confirmed = "confirmed"
    upcoming = "upcoming"
    seated = "seated"
    cancelled = "cancelled"
    no_show = "no-show"


class TableStatus(str, Enum):
    free = "free"
    occupied = "occupied"
    reserved = "reserved"


class AnalyticsRange(str, Enum):
    daily = "daily"
    weekly = "weekly"


class SmsReply(str, Enum):
    YES = "YES"
    CANCEL = "CANCEL"
    CONFIRM = "CONFIRM"


class Settings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    restaurantName: str = Field(min_length=1)
    gracePeriodMinutes: int = Field(ge=1, le=30)


class UpdateSettingsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    restaurantName: str | None = Field(default=None, min_length=1)
    gracePeriodMinutes: int | None = Field(default=None, ge=1, le=30)


class Party(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    phone: str
    partySize: int
    notes: str
    source: PartySource
    status: PartyStatus
    position: int | None = None
    queuedAt: str
    reservationTime: str | None = None
    tableId: str | None = None
    notifiedAt: str | None = None
    seatedAt: str | None = None
    seatedWaitMinutes: int | None = None
    waitEstimateMinutes: int | None = None


class Table(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    seats: int
    x: float
    y: float
    w: float
    h: float
    status: TableStatus
    partyId: str | None
    occupiedAt: str | None
    partyName: str | None


class SmsMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    partyId: str
    direction: Literal["inbound", "outbound"]
    kind: Literal["join", "ready", "confirm", "cancel", "noshow", "seated"]
    body: str
    at: str


class HostNotice(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    at: str
    text: str


class Snapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    now: str
    settings: Settings
    tables: list[Table]
    parties: list[Party]
    queue: list[Party]
    upcoming: list[Party]
    sms: list[SmsMessage]
    hostNotices: list[HostNotice]


class GuestJoinRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    phone: str = Field(min_length=1)
    partySize: int = Field(ge=1, le=12)
    notes: str = ""


class AddPartyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    phone: str = Field(min_length=1)
    partySize: int = Field(ge=1, le=12)
    notes: str = ""
    source: PartySource = PartySource.walk_in
    reservationTime: str | None = None
    tableId: str | None = None


class UpdatePartyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1)
    phone: str | None = Field(default=None, min_length=1)
    partySize: int | None = Field(default=None, ge=1, le=12)
    notes: str | None = None
    reservationTime: str | None = None


class SeatPartyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tableId: str


class SmsReplyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reply: SmsReply


class ReorderQueueRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fromPosition: int = Field(ge=1)
    toPosition: int = Field(ge=1)


class SetTableStatusRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: TableStatus


class InboundSmsWebhook(BaseModel):
    model_config = ConfigDict(extra="allow")

    from_: str = Field(alias="from")
    body: str


class WebhookAck(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: Literal[True] = True
    partyId: str | None = None


class ErrorResponse(BaseModel):
    error: str
    code: str | None = None
