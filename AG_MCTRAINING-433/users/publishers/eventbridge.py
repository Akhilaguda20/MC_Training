import json
import logging

logger = logging.getLogger(__name__)


class EventBridgePublisher:
    """
    Concrete publisher backed by AWS EventBridge.
    Client and bus name are injected — no boto3.client() calls inside.
    """

    def __init__(self, client, event_bus_name: str) -> None:
        self._client = client
        self._bus = event_bus_name

    def publish(self, detail_type: str, detail: dict) -> None:
        logger.info(
            "Publishing EventBridge event",
            extra={
                "event_bus": self._bus,
                "detail_type": detail_type,
                "detail": detail,
            },
        )

        response = self._client.put_events(
            Entries=[
                {
                    "Source": "user.service",
                    "DetailType": detail_type,
                    "Detail": json.dumps(detail),
                    "EventBusName": self._bus,
                }
            ]
        )

        failed = response.get("FailedEntryCount", 0)
        if failed:
            for entry in response.get("Entries", []):
                if entry.get("ErrorCode"):
                    logger.error(
                        "EventBridge entry failed",
                        extra={
                            "event_bus": self._bus,
                            "detail_type": detail_type,
                            "error_code": entry["ErrorCode"],
                            "error_message": entry.get("ErrorMessage"),
                        },
                    )
            raise RuntimeError(
                f"EventBridge put_events failed for {detail_type!r}: "
                f"{failed} entr{'y' if failed == 1 else 'ies'} rejected"
            )

        logger.info(
            "EventBridge event accepted",
            extra={
                "event_bus": self._bus,
                "detail_type": detail_type,
                "event_id": response["Entries"][0].get("EventId"),
            },
        )
