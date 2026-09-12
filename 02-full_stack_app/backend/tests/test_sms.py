def test_notify_ready(client):
    response = client.post("/v1/parties/p1/notify")
    assert response.status_code == 200
    party = next(p for p in response.json()["queue"] if p["id"] == "p1")
    assert party["status"] == "notified"
    assert party["notifiedAt"] is not None


def test_notify_ready_not_waiting_returns_409(client):
    response = client.post("/v1/parties/p5/notify")
    assert response.status_code == 409


def test_sms_reply_confirm(client):
    response = client.post("/v1/parties/p3/sms-reply", json={"reply": "YES"})
    assert response.status_code == 200
    party = next(p for p in response.json()["queue"] if p["id"] == "p3")
    assert party["status"] == "confirmed"


def test_sms_reply_cancel(client):
    notify = client.post("/v1/parties/p1/notify")
    assert notify.status_code == 200
    response = client.post("/v1/parties/p1/sms-reply", json={"reply": "CANCEL"})
    assert response.status_code == 200
    assert not any(party["id"] == "p1" for party in response.json()["queue"])


def test_webhook_sms_confirm(client):
    response = client.post(
        "/v1/webhooks/sms",
        json={"from": "555-0103", "body": "yes"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["partyId"] == "p3"


def test_webhook_sms_unknown_phone_returns_404(client):
    response = client.post(
        "/v1/webhooks/sms",
        json={"from": "555-9999", "body": "YES"},
    )
    assert response.status_code == 404


def test_auto_no_show_after_grace_period(client, clock):
    clock.advance_minutes(8)
    response = client.get("/v1/snapshot")
    assert response.status_code == 200
    snap = response.json()
    assert not any(party["id"] == "p3" for party in snap["queue"])
    p3 = next(p for p in snap["parties"] if p["id"] == "p3")
    assert p3["status"] == "no-show"
    assert snap["hostNotices"][0]["text"].lower().find("no-show") >= 0
