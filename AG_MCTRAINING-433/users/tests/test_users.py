"""
tests/test_users.py

Tests at two levels:
  1. Service unit tests — UserService + in-memory fakes, zero HTTP/AWS.
  2. Route integration tests — FastAPI TestClient + dependency_overrides,
     zero boto3 calls.

No patching. No mocks. Pure dependency injection.
"""

import pytest
from fastapi.testclient import TestClient

from users.core.dependencies import get_user_service
from users.main import app
from users.repositories.dynamodb import DynamoDBUserRepository
from users.services.user_service import UserService
from users.tests.conftest import FakeEventPublisher, InMemoryUserRepository


# Helpers                                                                      #

def make_service(repo=None, publisher=None) -> UserService:
    """Build a UserService backed entirely by in-memory fakes."""
    return UserService(
        repo=repo or InMemoryUserRepository(),
        publisher=publisher or FakeEventPublisher(),
    )


# 1. UserService — unit tests (no FastAPI, no HTTP)                           #

class TestUserServiceCreate:
    def test_generates_uuid_when_user_id_not_provided(self):
        repo = InMemoryUserRepository()
        service = make_service(repo=repo)

        user_id = service.create_user({"name": "Alice", "email": "a@b.com"})

        assert user_id is not None
        assert len(user_id) == 36  # UUID4 format
        assert repo.get(user_id) is not None

    def test_uses_provided_user_id(self):
        repo = InMemoryUserRepository()
        service = make_service(repo=repo)

        user_id = service.create_user({"userId": "u-001", "name": "Bob", "email": "b@b.com"})

        assert user_id == "u-001"
        assert repo.get("u-001")["name"] == "Bob"

    def test_publishes_user_created_event(self):
        publisher = FakeEventPublisher()
        service = make_service(publisher=publisher)

        service.create_user({"name": "Alice", "email": "a@b.com"})

        assert len(publisher.events) == 1
        assert publisher.events[0]["detail_type"] == "UserCreated"


class TestUserServiceGet:
    def test_returns_user_when_exists(self):
        repo = InMemoryUserRepository()
        service = make_service(repo=repo)
        service.create_user({"userId": "u-1", "name": "Alice", "email": "a@b.com"})

        result = service.get_user("u-1")

        assert result is not None
        assert result["userId"] == "u-1"

    def test_returns_none_when_not_found(self):
        service = make_service()
        assert service.get_user("nonexistent") is None


class TestUserServiceUpdate:
    def test_publishes_user_updated_event(self):
        publisher = FakeEventPublisher()
        service = make_service(publisher=publisher)

        service.update_user("u-1", {"name": "Alice Updated"})

        assert publisher.events[0]["detail_type"] == "UserUpdated"
        assert publisher.events[0]["detail"]["userId"] == "u-1"


class TestUserServiceDelete:
    def test_publishes_event_and_removes_from_repo(self):
        repo = InMemoryUserRepository()
        publisher = FakeEventPublisher()
        service = make_service(repo=repo, publisher=publisher)
        service.create_user({"userId": "u-del", "name": "Delete Me", "email": "d@b.com"})

        service.delete_user("u-del")

        assert repo.get("u-del") is None
        assert publisher.events[-1]["detail_type"] == "UserDeleted"


# 2. DynamoDBUserRepository — unit tests with injected mock client            #

class TestDynamoDBUserRepository:
    def _repo(self, mock_client):
        return DynamoDBUserRepository(mock_client, "test-table")

    def test_create_calls_put_item(self, mocker):
        mock_client = mocker.MagicMock()
        repo = self._repo(mock_client)

        repo.create("u-1", {"name": "Alice", "email": "a@b.com"})

        mock_client.put_item.assert_called_once()
        call_kwargs = mock_client.put_item.call_args.kwargs
        assert call_kwargs["TableName"] == "test-table"
        assert call_kwargs["Item"]["userId"] == {"S": "u-1"}
        assert call_kwargs["Item"]["name"] == {"S": "Alice"}

    def test_get_returns_flattened_dict_when_item_found(self, mocker):
        mock_client = mocker.MagicMock()
        mock_client.get_item.return_value = {
            "Item": {
                "userId": {"S": "u-1"},
                "name":   {"S": "Alice"},
                "status": {"S": "CREATED"},
            }
        }
        repo = self._repo(mock_client)

        result = repo.get("u-1")

        assert result == {"userId": "u-1", "name": "Alice", "status": "CREATED"}

    def test_get_returns_none_when_item_not_found(self, mocker):
        mock_client = mocker.MagicMock()
        mock_client.get_item.return_value = {}  # no "Item" key
        repo = self._repo(mock_client)

        assert repo.get("missing") is None

    def test_update_calls_update_item_with_system_when_no_data(self, mocker):
        mock_client = mocker.MagicMock()
        repo = self._repo(mock_client)

        repo.update("u-1", data=None)

        ev = mock_client.update_item.call_args.kwargs["ExpressionAttributeValues"]
        assert ev[":m"] == {"S": "system"}

    def test_update_extracts_updated_by_from_data(self, mocker):
        mock_client = mocker.MagicMock()
        repo = self._repo(mock_client)

        repo.update("u-1", data={"updatedBy": "admin"})

        ev = mock_client.update_item.call_args.kwargs["ExpressionAttributeValues"]
        assert ev[":m"] == {"S": "admin"}

    def test_delete_calls_delete_item(self, mocker):
        mock_client = mocker.MagicMock()
        repo = self._repo(mock_client)

        repo.delete("u-1")

        mock_client.delete_item.assert_called_once_with(
            TableName="test-table",
            Key={"userId": {"S": "u-1"}},
        )


# 3. Route integration tests — FastAPI TestClient + dependency_overrides      #

@pytest.fixture
def client():
    """
    TestClient with dependency_overrides injecting in-memory fakes.
    No boto3, no network, no patching.
    """
    repo = InMemoryUserRepository()
    publisher = FakeEventPublisher()
    service = UserService(repo, publisher)

    app.dependency_overrides[get_user_service] = lambda: service
    yield TestClient(app), repo, publisher
    app.dependency_overrides.clear()


class TestCreateUserRoute:
    def test_returns_201_with_user_id(self, client):
        http, _, _ = client
        response = http.post("/api/v1/users", json={"name": "Alice", "email": "a@b.com"})
        assert response.status_code == 201
        assert "userId" in response.json()

    def test_uses_provided_user_id(self, client):
        http, repo, _ = client
        response = http.post(
            "/api/v1/users",
            json={"userId": "u-fixed", "name": "Bob", "email": "b@b.com"},
        )
        assert response.status_code == 201
        assert response.json()["userId"] == "u-fixed"
        assert repo.get("u-fixed") is not None


class TestGetUserRoute:
    def test_returns_200_with_user_data(self, client):
        http, repo, _ = client
        repo.create("u-get", {"name": "Alice", "email": "a@b.com"})

        response = http.get("/api/v1/users/u-get")

        assert response.status_code == 200
        assert response.json()["userId"] == "u-get"

    def test_returns_404_when_not_found(self, client):
        http, _, _ = client
        response = http.get("/api/v1/users/nobody")
        assert response.status_code == 404


class TestUpdateUserRoute:
    def test_returns_200_and_publishes_event(self, client):
        http, _, publisher = client
        response = http.put("/api/v1/users/u-1", json={"name": "Updated"})
        assert response.status_code == 200
        assert response.json() == {"message": "Event sent"}
        assert any(e["detail_type"] == "UserUpdated" for e in publisher.events)


class TestDeleteUserRoute:
    def test_returns_200_and_removes_user(self, client):
        http, repo, _ = client
        repo.create("u-del", {"name": "Gone", "email": "g@b.com"})

        response = http.delete("/api/v1/users/u-del")

        assert response.status_code == 200
        assert repo.get("u-del") is None


class TestListUsersRoute:
    def test_returns_empty_list_when_no_users(self, client):
        http, _, _ = client
        response = http.get("/api/v1/users")
        assert response.status_code == 200
        assert response.json() == []

    def test_returns_all_users(self, client):
        http, repo, _ = client
        repo.create("u-a", {"name": "Alice", "email": "a@b.com"})
        repo.create("u-b", {"name": "Bob", "email": "b@b.com"})

        response = http.get("/api/v1/users")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        ids = {u["userId"] for u in data}
        assert ids == {"u-a", "u-b"}


class TestUserServiceListUsers:
    def test_returns_all_users_from_repo(self):
        repo = InMemoryUserRepository()
        service = make_service(repo=repo)
        service.create_user({"userId": "u-1", "name": "Alice", "email": "a@b.com"})
        service.create_user({"userId": "u-2", "name": "Bob", "email": "b@b.com"})

        result = service.list_users()

        assert len(result) == 2

    def test_returns_empty_list_when_no_users(self):
        service = make_service()
        assert service.list_users() == []
