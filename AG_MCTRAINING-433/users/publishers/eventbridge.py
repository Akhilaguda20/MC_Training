import json


class EventBridgePublisher:
    """
    Concrete publisher backed by AWS EventBridge.
    Client and bus name are injected — no boto3.client() calls inside.
    """

    def __init__(self, client, event_bus_name: str) -> None:
        self._client = client
        self._bus = event_bus_name

    def publish(self, detail_type: str, detail: dict) -> None:
        self._client.put_events(
            Entries=[
                {
                    "Source": "user.service",
                    "DetailType": detail_type,
                    "Detail": json.dumps(detail),
                    "EventBusName": self._bus,
                }
            ]
        )
