"""
tests/test_publishers.py

Covers: users/publishers/eventbridge.py — EventBridgePublisher.__init__ and publish().
Client is injected — no boto3 dependency needed.
"""

import json

from users.publishers.eventbridge import EventBridgePublisher


class TestEventBridgePublisher:
    def test_publish_calls_put_events_with_correct_entry(self, mocker):
        mock_client = mocker.MagicMock()
        publisher = EventBridgePublisher(mock_client, "test-bus")

        publisher.publish("UserCreated", {"userId": "u-1", "name": "Alice"})

        mock_client.put_events.assert_called_once()
        entry = mock_client.put_events.call_args.kwargs["Entries"][0]
        assert entry["Source"] == "user.service"
        assert entry["DetailType"] == "UserCreated"
        assert entry["EventBusName"] == "test-bus"
        assert json.loads(entry["Detail"]) == {"userId": "u-1", "name": "Alice"}

    def test_publish_serialises_detail_as_json(self, mocker):
        mock_client = mocker.MagicMock()
        publisher = EventBridgePublisher(mock_client, "bus")

        publisher.publish("UserDeleted", {"userId": "u-99"})

        entry = mock_client.put_events.call_args.kwargs["Entries"][0]
        # Detail must be a string (JSON), not a dict
        assert isinstance(entry["Detail"], str)
        assert json.loads(entry["Detail"])["userId"] == "u-99"
