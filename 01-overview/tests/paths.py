"""Shared paths for tests outside the Django app package."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
APP_DIR = PROJECT_ROOT / "homework_quest"
STATIC_DIR = APP_DIR / "static" / "homework_quest"
