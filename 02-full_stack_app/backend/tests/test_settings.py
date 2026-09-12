def test_update_settings(client):
    response = client.patch(
        "/v1/settings",
        json={"gracePeriodMinutes": 10},
    )
    assert response.status_code == 200
    assert response.json()["settings"]["gracePeriodMinutes"] == 10


def test_reset_demo(client):
    response = client.post("/v1/demo/reset")
    assert response.status_code == 200
    snap = response.json()
    assert snap["settings"]["restaurantName"] == "Waitly Bistro"
    assert len(snap["queue"]) == 4
