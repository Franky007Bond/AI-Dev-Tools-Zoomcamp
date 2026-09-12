def test_add_walk_in_returns_snapshot_and_join_sms(client):
    response = client.post(
        "/v1/parties",
        json={"name": "Rivera", "phone": "555-0199", "partySize": 3, "notes": ""},
    )
    assert response.status_code == 200
    snap = response.json()
    assert snap["queue"][-1]["name"] == "Rivera"
    assert snap["sms"][0]["body"].find("Rivera party of 3") >= 0


def test_join_guest_returns_party_not_snapshot(client):
    response = client.post(
        "/v1/join",
        json={"name": "Lee", "phone": "555-0200", "partySize": 2},
    )
    assert response.status_code == 201
    party = response.json()
    assert party["name"] == "Lee"
    assert party["source"] == "remote"
    assert party["status"] == "waiting"
    assert "id" in party


def test_future_reservation_stays_upcoming_and_holds_table(client):
    later = "2026-09-09T21:00:00.000Z"
    response = client.post(
        "/v1/parties",
        json={
            "name": "Adler",
            "phone": "555-0188",
            "partySize": 2,
            "source": "reservation",
            "reservationTime": later,
            "tableId": "t2",
        },
    )
    assert response.status_code == 200
    snap = response.json()
    assert not any(party["name"] == "Adler" for party in snap["queue"])
    assert snap["upcoming"][0]["name"] == "Adler"
    t2 = next(table for table in snap["tables"] if table["id"] == "t2")
    assert t2["status"] == "reserved"


def test_add_party_rejects_occupied_table(client):
    response = client.post(
        "/v1/parties",
        json={
            "name": "Test",
            "phone": "555-0001",
            "partySize": 2,
            "tableId": "t1",
        },
    )
    assert response.status_code == 409
    assert "error" in response.json()


def test_update_party(client):
    response = client.patch(
        "/v1/parties/p2",
        json={"notes": "High chair"},
    )
    assert response.status_code == 200
    party = next(p for p in response.json()["parties"] if p["id"] == "p2")
    assert party["notes"] == "High chair"


def test_update_party_not_found(client):
    response = client.patch("/v1/parties/p99", json={"notes": "x"})
    assert response.status_code == 404


def test_remove_party(client):
    response = client.delete("/v1/parties/p2")
    assert response.status_code == 200
    snap = response.json()
    assert not any(party["id"] == "p2" for party in snap["queue"])
    cancelled = next(p for p in snap["parties"] if p["id"] == "p2")
    assert cancelled["status"] == "cancelled"
