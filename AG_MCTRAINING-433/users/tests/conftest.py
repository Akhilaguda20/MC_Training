"""
conftest.py — shared fixtures for all tests.

Environment variables are set HERE, before any app module is imported.
Because app/core/config.py uses @property (reads os.environ on each access),
setting them here is sufficient — no global patching of boto3 needed.
"""

import os

import pytest

os.environ.setdefault("TABLE_NAME", "test-table")
os.environ.setdefault("EVENT_BUS_NAME", "test-event-bus")

class InMemoryUserRepository:
    """A dict-backed UserRepository — no boto3, no DynamoDB, no mocking."""

    def __init__(self):
        self._store: dict = {}

    def create(self, user_id: str, data: dict) -> None:
        self._store[user_id] = {"userId": user_id, **data, "status": "CREATED"}

    def get(self, user_id: str):
        return self._store.get(user_id)

    def update(self, user_id: str, data=None) -> None:
        if user_id in self._store:
            self._store[user_id]["status"] = "UPDATED"

    def delete(self, user_id: str) -> None:
        self._store.pop(user_id, None)


class FakeEventPublisher:

    def __init__(self):
        self.events: list[dict] = []

    def publish(self, detail_type: str, detail: dict) -> None:
        self.events.append({"detail_type": detail_type, "detail": detail})


# --------------------------------------------------------------------------- #
# Pytest fixtures                                                              #
# --------------------------------------------------------------------------- #

@pytest.fixture
def fake_repo():
    return InMemoryUserRepository()


@pytest.fixture
def fake_publisher():
    return FakeEventPublisher()
