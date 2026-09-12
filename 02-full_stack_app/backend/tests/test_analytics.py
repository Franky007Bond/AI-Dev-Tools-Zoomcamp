def test_daily_analytics(client):
    response = client.get("/v1/analytics")
    assert response.status_code == 200
    data = response.json()
    assert data["range"] == "daily"
    assert data["partiesSeated"] > 0
    assert data["averageWaitMinutes"] > 0
    assert data["noShowRate"] >= 0
    assert any(row["count"] > 0 for row in data["busiestHours"])
    assert len(data["busiestDays"]) == 7


def test_weekly_analytics(client):
    response = client.get("/v1/analytics?range=weekly")
    assert response.status_code == 200
    assert response.json()["range"] == "weekly"
