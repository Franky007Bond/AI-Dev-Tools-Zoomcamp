"""
Offline queue payload validation (mirrors homework_quest/static/homework_quest/offline_queue.js).

Payload shape stored in localStorage under key ``homework_quest_offline_queue_v1``:

{
  "version": 1,
  "items": [
    {
      "id": "<unique string>",
      "kind": "approve" | "log-form",
      "url": "<POST url>",
      "method": "POST",
      "contentType": "json" | "form",
      "body": { ... },
      "createdAt": "<ISO-8601>"
    }
  ]
}

``approve`` body: {"approver_id": int, "pin": "1234"}
``log-form`` body: {"profile_id": str, "pin": "1234", "csrfmiddlewaretoken": str}
"""

from __future__ import annotations

VALID_KINDS = frozenset({"approve", "log-form"})
VALID_CONTENT_TYPES = frozenset({"json", "form"})


class OfflineQueueError(Exception):
    pass


def validate_queue_item(item: dict) -> dict:
    if not isinstance(item, dict):
        raise OfflineQueueError("Queue item must be an object.")
    kind = item.get("kind")
    if kind not in VALID_KINDS:
        raise OfflineQueueError(f"Unsupported kind: {kind!r}")
    if not item.get("url"):
        raise OfflineQueueError("Queue item requires url.")
    content_type = item.get("contentType")
    if content_type not in VALID_CONTENT_TYPES:
        raise OfflineQueueError(f"Unsupported contentType: {content_type!r}")
    body = item.get("body")
    if not isinstance(body, dict):
        raise OfflineQueueError("Queue item body must be an object.")
    if kind == "approve":
        if "approver_id" not in body or "pin" not in body:
            raise OfflineQueueError("Approve payload requires approver_id and pin.")
    if kind == "log-form":
        for key in ("profile_id", "pin"):
            if key not in body:
                raise OfflineQueueError(f"log-form payload requires {key}.")
    return item


def validate_queue_document(document: dict) -> dict:
    if document.get("version") != 1:
        raise OfflineQueueError("Unsupported queue version.")
    items = document.get("items")
    if not isinstance(items, list):
        raise OfflineQueueError("Queue items must be a list.")
    for item in items:
        validate_queue_item(item)
    return document
