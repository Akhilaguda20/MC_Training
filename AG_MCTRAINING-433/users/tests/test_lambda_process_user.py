"""
tests/test_lambda_process_user.py

Covers: lambdas/process_user/handler.py — lambda_handler().

The handler creates a DynamoDBUserRepository using get_dynamodb_client().
We patch get_dynamodb_client at the handler-module level so the injected
mock client flows into the repository without touching real AWS.
"""

import json

import pytest

from lambdas.process_user.handler import lambda_handler


def _make_sqs_event(records: list) -> dict:
    return {"Records": [{"body": json.dumps(r)} for r in records]}


class TestProcessUserLambdaHandler:
    def test_calls_update_item_for_single_record(self, mocker):
        mock_client = mocker.MagicMock() # act as fake boto3 DynamoDB client 
        mocker.patch(
            "lambdas.process_user.handler.get_dynamodb_client",
            return_value=mock_client,
        )

        event = _make_sqs_event([
            {"detail": {"userId": "u-1", "data": {"updatedBy": "admin"}}}
        ])
        lambda_handler(event, {})

        mock_client.update_item.assert_called_once()
        call_kwargs = mock_client.update_item.call_args.kwargs
        assert call_kwargs["Key"] == {"userId": {"S": "u-1"}}

    def test_calls_update_item_for_each_record(self, mocker):
        mock_client = mocker.MagicMock()
        mocker.patch(
            "lambdas.process_user.handler.get_dynamodb_client",
            return_value=mock_client,
        )

        event = _make_sqs_event([
            {"detail": {"userId": "u-1", "data": {}}},
            {"detail": {"userId": "u-2", "data": {}}},
        ])
        lambda_handler(event, {})

        assert mock_client.update_item.call_count == 2

    def test_uses_system_as_last_modified_by_when_no_updated_by(self, mocker):
        mock_client = mocker.MagicMock()
        mocker.patch(
            "lambdas.process_user.handler.get_dynamodb_client",
            return_value=mock_client,
        )

        event = _make_sqs_event([
            {"detail": {"userId": "u-1", "data": {}}}
        ])
        lambda_handler(event, {})

        ev = mock_client.update_item.call_args.kwargs["ExpressionAttributeValues"]
        assert ev[":m"] == {"S": "system"}
