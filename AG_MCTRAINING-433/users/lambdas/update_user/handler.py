"""
Lambda handler — triggered by API Gateway (PUT /user/{id}).

Publishes a "UserUpdated" event to EventBridge.
The actual DynamoDB write is handled asynchronously by the
process_user Lambda after the event travels through SQS.
"""

import json
import logging

from users.core.config import settings
from users.db.session import get_eventbridge_client
from users.publishers.eventbridge import EventBridgePublisher
from users.utils.response import build_response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _log(level: str, event: str, **kwargs) -> None:
    logger.log(
        getattr(logging, level),
        json.dumps({"event": event, **kwargs}),
    )


def lambda_handler(event: dict, context) -> dict:
    try:
        user_id = event["pathParameters"]["id"]
    except (KeyError, TypeError):
        return build_response(400, {"message": "Missing path parameter: id"})

    raw_body = event.get("body") or "{}"
    try:
        body = json.loads(raw_body)
    except json.JSONDecodeError:
        return build_response(400, {"message": "Invalid JSON body"})

    try:
        publisher = EventBridgePublisher(
            client=get_eventbridge_client(),
            event_bus_name=settings.EVENT_BUS_NAME,
        )
        publisher.publish("UserUpdated", {"userId": user_id, "data": body})
        _log("INFO", "user_updated_event_published", user_id=user_id)
    except Exception as exc:
        _log("ERROR", "publish_failed", user_id=user_id, error=str(exc))
        return build_response(500, {"message": "Internal server error"})

    return build_response(200, {"message": "Event sent"})
