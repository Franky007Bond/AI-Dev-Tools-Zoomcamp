from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable

from fastapi import Depends, FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.errors import WaitlyError
from backend.schemas import (
    AddPartyRequest,
    AnalyticsRange,
    GuestJoinRequest,
    InboundSmsWebhook,
    ReorderQueueRequest,
    SeatPartyRequest,
    SetTableStatusRequest,
    SmsReplyRequest,
    UpdatePartyRequest,
    UpdateSettingsRequest,
    WebhookAck,
)
from backend.service import WaitlyService
from backend.store import MockStore


def create_app(
    store: MockStore | None = None,
    now_fn: Callable[[], datetime] | None = None,
) -> FastAPI:
    app = FastAPI(title="Waitly API", version="1.0.0")
    state_store = store or MockStore.create_seed()
    state_now_fn = now_fn or (lambda: datetime.now(timezone.utc))

    def get_service() -> WaitlyService:
        return WaitlyService(state_store, state_now_fn)

    @app.exception_handler(WaitlyError)
    async def waitly_error_handler(_request: Request, exc: WaitlyError) -> JSONResponse:
        payload: dict[str, str] = {"error": exc.message}
        if exc.code:
            payload["code"] = exc.code
        return JSONResponse(status_code=exc.status_code, content=payload)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
        detail = exc.errors()[0]["msg"] if exc.errors() else "Validation error"
        return JSONResponse(status_code=422, content={"error": detail})

    @app.get("/v1/snapshot")
    def get_snapshot(service: WaitlyService = Depends(get_service)):
        return service.snapshot()

    @app.post("/v1/join", status_code=201)
    def join_waitlist(body: GuestJoinRequest, service: WaitlyService = Depends(get_service)):
        return service.join_waitlist(body.model_dump())

    @app.post("/v1/parties")
    def add_party(body: AddPartyRequest, service: WaitlyService = Depends(get_service)):
        source = body.source.value if hasattr(body.source, "value") else body.source
        payload = body.model_dump()
        payload["source"] = source
        return service.add_party_snapshot(payload)

    @app.patch("/v1/parties/{party_id}")
    def update_party(
        party_id: str,
        body: UpdatePartyRequest,
        service: WaitlyService = Depends(get_service),
    ):
        patch = body.model_dump(exclude_unset=True)
        if not patch:
            raise WaitlyError("No fields to update", status_code=422, code="empty_patch")
        return service.update_party(party_id, patch)

    @app.delete("/v1/parties/{party_id}")
    def remove_party(party_id: str, service: WaitlyService = Depends(get_service)):
        return service.remove_party(party_id)

    @app.post("/v1/parties/{party_id}/notify")
    def notify_ready(party_id: str, service: WaitlyService = Depends(get_service)):
        return service.notify_ready(party_id)

    @app.post("/v1/parties/{party_id}/seat")
    def seat_party(
        party_id: str,
        body: SeatPartyRequest,
        service: WaitlyService = Depends(get_service),
    ):
        return service.seat_party(party_id, body.tableId)

    @app.post("/v1/parties/{party_id}/sms-reply")
    def sms_reply(
        party_id: str,
        body: SmsReplyRequest,
        service: WaitlyService = Depends(get_service),
    ):
        return service.sms_reply(party_id, body.reply.value)

    @app.post("/v1/queue/reorder")
    def reorder_queue(body: ReorderQueueRequest, service: WaitlyService = Depends(get_service)):
        return service.reorder_queue(body.fromPosition, body.toPosition)

    @app.patch("/v1/tables/{table_id}")
    def set_table_status(
        table_id: str,
        body: SetTableStatusRequest,
        service: WaitlyService = Depends(get_service),
    ):
        return service.set_table_status(table_id, body.status.value)

    @app.post("/v1/webhooks/sms")
    def receive_sms(body: InboundSmsWebhook, service: WaitlyService = Depends(get_service)):
        _snap, party_id = service.receive_sms(body.from_, body.body)
        return WebhookAck(ok=True, partyId=party_id)

    @app.get("/v1/analytics")
    def get_analytics(
        range: AnalyticsRange = Query(default=AnalyticsRange.daily),
        service: WaitlyService = Depends(get_service),
    ):
        return service.get_analytics(range.value)

    @app.patch("/v1/settings")
    def update_settings(body: UpdateSettingsRequest, service: WaitlyService = Depends(get_service)):
        patch = body.model_dump(exclude_unset=True)
        if not patch:
            raise WaitlyError("No fields to update", status_code=422, code="empty_patch")
        return service.update_settings(patch)

    @app.post("/v1/demo/reset")
    def reset_demo(service: WaitlyService = Depends(get_service)):
        return service.reset_demo()

    return app


app = create_app()


def run() -> None:
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
