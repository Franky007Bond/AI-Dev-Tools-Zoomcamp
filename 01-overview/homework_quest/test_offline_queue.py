import pytest

from homework_quest.offline_queue import OfflineQueueError, validate_queue_document, validate_queue_item


def test_validate_approve_payload():
    item = validate_queue_item(
        {
            "kind": "approve",
            "url": "/api/chores/1/approve/",
            "contentType": "json",
            "body": {"approver_id": 2, "pin": "5678"},
        }
    )
    assert item["kind"] == "approve"


def test_validate_log_form_payload():
    item = validate_queue_item(
        {
            "kind": "log-form",
            "url": "/chore-pool/log-routine/1/",
            "contentType": "form",
            "body": {"profile_id": "1", "pin": "1234", "csrfmiddlewaretoken": "abc"},
        }
    )
    assert item["contentType"] == "form"


def test_validate_rejects_missing_pin():
    with pytest.raises(OfflineQueueError):
        validate_queue_item(
            {
                "kind": "approve",
                "url": "/api/chores/1/approve/",
                "contentType": "json",
                "body": {"approver_id": 2},
            }
        )


def test_validate_queue_document():
    doc = validate_queue_document(
        {
            "version": 1,
            "items": [
                {
                    "kind": "approve",
                    "url": "/api/chores/1/approve/",
                    "contentType": "json",
                    "body": {"approver_id": 2, "pin": "5678"},
                }
            ],
        }
    )
    assert len(doc["items"]) == 1
