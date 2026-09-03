from homework_quest.settings import *  # noqa: F401, F403

# Isolated from the developer's db.sqlite3; pytest-django creates this in-process.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
