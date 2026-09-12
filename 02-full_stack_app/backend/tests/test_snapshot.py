def test_get_snapshot_returns_unified_queue_with_estimates(client):
    response = client.get("/v1/snapshot")
    assert response.status_code == 200
    snap = response.json()
    assert [party["name"] for party in snap["queue"]] == [
        "Nguyen",
        "Patel",
        "Garcia",
        "Okoye",
    ]
    assert snap["queue"][0]["waitEstimateMinutes"] > 0
    t5 = next(table for table in snap["tables"] if table["id"] == "t5")
    assert t5["status"] == "reserved"
    assert "now" in snap
    assert "settings" in snap
    assert "sms" in snap
    assert "hostNotices" in snap
