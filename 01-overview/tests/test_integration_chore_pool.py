import pytest
from django.test import Client

from homework_quest.models import ChoreInstance, ChoreStatus
from homework_quest.xp import xp_from_minutes


@pytest.fixture
def client():
    return Client(enforce_csrf_checks=False)


@pytest.mark.django_db
def test_create_adhoc_bounty_from_pool(client):
    minutes = 25
    expected_xp = xp_from_minutes(minutes)

    response = client.post(
        "/chore-pool/bounty/",
        data={
            "title": "Clean garage",
            "category": "Outdoor",
            "estimated_minutes": minutes,
        },
    )
    assert response.status_code == 302
    assert response.url.endswith("/chore-pool/?tab=bounties")

    chore = ChoreInstance.objects.get(title="Clean garage")
    assert chore.status == ChoreStatus.OPEN
    assert chore.xp_value == expected_xp
    assert chore.assignee_id is None

    pool_response = client.get("/chore-pool/?tab=bounties")
    assert pool_response.status_code == 200
    html = pool_response.content.decode()
    assert "Clean garage" in html
    assert f"{expected_xp} XP" in html
