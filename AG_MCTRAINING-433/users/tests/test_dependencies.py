"""
tests/test_dependencies.py

Covers: users/core/dependencies.py — get_user_service().
The factory is patched at the db-session level so no real boto3 calls are made.
"""

from users.core.dependencies import get_user_service
from users.services.user_service import UserService


class TestGetUserService:
    def test_returns_user_service_instance(self, mocker):
        mocker.patch(
            "users.core.dependencies.get_dynamodb_client",
            return_value=mocker.MagicMock(),
        )
        mocker.patch(
            "users.core.dependencies.get_eventbridge_client",
            return_value=mocker.MagicMock(),
        )

        service = get_user_service()

        assert isinstance(service, UserService)
