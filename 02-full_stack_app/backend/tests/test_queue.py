def test_reorder_queue(client):
    response = client.post(
        "/v1/queue/reorder",
        json={"fromPosition": 1, "toPosition": 2},
    )
    assert response.status_code == 200
    names = [party["name"] for party in response.json()["queue"][:2]]
    assert names == ["Patel", "Nguyen"]


def test_reorder_invalid_position_returns_422(client):
    response = client.post(
        "/v1/queue/reorder",
        json={"fromPosition": 1, "toPosition": 99},
    )
    assert response.status_code == 422
