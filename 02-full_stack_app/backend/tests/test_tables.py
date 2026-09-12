def test_seat_party_on_free_table(client):
    response = client.post(
        "/v1/parties/p1/seat",
        json={"tableId": "t2"},
    )
    assert response.status_code == 200
    snap = response.json()
    assert not any(party["id"] == "p1" for party in snap["queue"])
    table = next(item for item in snap["tables"] if item["id"] == "t2")
    assert table["status"] == "occupied"
    assert table["partyName"] == "Nguyen"


def test_seat_party_on_occupied_table_returns_409(client):
    response = client.post(
        "/v1/parties/p2/seat",
        json={"tableId": "t1"},
    )
    assert response.status_code == 409


def test_set_table_free_may_auto_notify(client):
    response = client.patch("/v1/tables/t2", json={"status": "free"})
    assert response.status_code == 200
    assert response.json()["tables"]


def test_set_table_not_found(client):
    response = client.patch("/v1/tables/t99", json={"status": "free"})
    assert response.status_code == 404
