from pathlib import Path


def test_offline_queue_js_module_exists():
    path = Path(__file__).resolve().parent / "static" / "homework_quest" / "offline_queue.js"
    text = path.read_text(encoding="utf-8")
    assert "HomeworkQuestOfflineQueue" in text
    assert "localStorage" in text
    assert "homework_quest_offline_queue_v1" in text
