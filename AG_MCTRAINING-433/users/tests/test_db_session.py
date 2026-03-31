"""
tests/test_db_session.py

Covers: users/db/session.py — get_dynamodb_client() and get_eventbridge_client().
Both functions call boto3.client() — patched here so no real AWS call is made.
"""

import pytest

from users.db.session import get_dynamodb_client, get_eventbridge_client


class TestGetDynamodbClient:
    def test_returns_boto3_dynamodb_client(self, monkeypatch, mocker):
        monkeypatch.delenv("LOCALSTACK_URL", raising=False)
        mock_boto3 = mocker.patch("users.db.session.boto3")

        get_dynamodb_client()

        mock_boto3.client.assert_called_once_with(
            "dynamodb",
            endpoint_url=None,
            region_name="us-east-1",
        )


class TestGetEventbridgeClient:
    def test_returns_boto3_eventbridge_client(self, monkeypatch, mocker):
        monkeypatch.delenv("LOCALSTACK_URL", raising=False)
        mock_boto3 = mocker.patch("users.db.session.boto3")

        get_eventbridge_client()

        mock_boto3.client.assert_called_once_with(
            "events",
            endpoint_url=None,
            region_name="us-east-1",
        )
