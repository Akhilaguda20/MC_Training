"""
tests/test_db_session.py

Covers: payroll/db/session.py — get_dynamodb_client().
The function calls boto3.client() — patched here so no real AWS call is made.
"""

from payroll.db.session import get_dynamodb_client


class TestGetDynamodbClient:
    def test_returns_boto3_dynamodb_client(self, monkeypatch, mocker):
        monkeypatch.delenv("LOCALSTACK_URL", raising=False)
        mock_boto3 = mocker.patch("payroll.db.session.boto3")

        get_dynamodb_client()

        mock_boto3.client.assert_called_once_with(
            "dynamodb",
            endpoint_url=None,
            region_name="us-east-1",
        )
