"""
tests/test_lambda_update_user.py

Covers: lambdas/update_user/handler.py — lambda_handler().

The handler publishes an EventBridge event via EventBridgePublisher.
We patch get_eventbridge_client at the handler-module level so no real
AWS call is made.
"""

import json

from lambdas.update_user.handler import lambda_handler


def _make_apigw_event(user_id: str, body: dict) -> dict:
    return {
        "pathParameters": {"id": user_id},
        "body": json.dumps(body),
    }


class TestUpdateUserLambdaHandler:
    def test_returns_200_status_code(self, mocker):
        mock_client = mocker.MagicMock()
        mocker.patch(
            "lambdas.update_user.handler.get_eventbridge_client",
            return_value=mock_client,
        )

        result = lambda_handler(_make_apigw_event("u-1", {"name": "Alice"}), {})

        assert result["statusCode"] == 200

    def test_body_contains_event_sent_message(self, mocker):
        mock_client = mocker.MagicMock()
        mocker.patch(
            "lambdas.update_user.handler.get_eventbridge_client",
            return_value=mock_client,
        )

        result = lambda_handler(_make_apigw_event("u-1", {"name": "Alice"}), {})

        assert json.loads(result["body"]) == {"message": "Event sent"}

    def test_publishes_user_updated_event_to_eventbridge(self, mocker):
        mock_client = mocker.MagicMock()
        mocker.patch(
            "lambdas.update_user.handler.get_eventbridge_client",
            return_value=mock_client,
        )

        lambda_handler(_make_apigw_event("u-99", {"name": "Bob"}), {})

        mock_client.put_events.assert_called_once()
        entry = mock_client.put_events.call_args.kwargs["Entries"][0]
        assert entry["DetailType"] == "UserUpdated"
        detail = json.loads(entry["Detail"])
        assert detail["userId"] == "u-99"
        assert detail["data"]["name"] == "Bob"
