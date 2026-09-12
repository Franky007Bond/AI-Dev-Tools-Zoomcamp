from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from backend.main import create_app
from backend.store import MockStore

NOW = datetime(2026, 9, 9, 19, 0, 0, tzinfo=timezone.utc)


class TestClock:
    def __init__(self, initial: datetime = NOW) -> None:
        self.current = initial

    def __call__(self) -> datetime:
        return self.current

    def advance_minutes(self, minutes: int) -> None:
        from datetime import timedelta

        self.current += timedelta(minutes=minutes)


@pytest.fixture
def clock() -> TestClock:
    return TestClock()


@pytest.fixture
def store(clock: TestClock) -> MockStore:
    return MockStore.create_seed(now=clock())


@pytest.fixture
def client(store: MockStore, clock: TestClock) -> TestClient:
    app = create_app(store=store, now_fn=clock)
    return TestClient(app)
