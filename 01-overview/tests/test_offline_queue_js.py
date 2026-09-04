from tests.paths import STATIC_DIR


def test_offline_queue_js_module_exists():
    path = STATIC_DIR / "offline_queue.js"
    text = path.read_text(encoding="utf-8")
    assert "HomeworkQuestOfflineQueue" in text
    assert "localStorage" in text
    assert "homework_quest_offline_queue_v1" in text
