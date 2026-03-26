"""
Lambda handler — triggered by API Gateway (PUT /user/{id}).

Publishes a "UserUpdated" event to EventBridge.
The actual DynamoDB write is handled asynchronously by the
process_user Lambda after the event travels through SQS.
"""

import json
import os
import sys

if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):  # pragma: no cover
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "dependencies"))

from users.core.config import settings
from users.db.session import get_eventbridge_client
from users.publishers.eventbridge import EventBridgePublisher
from users.utils.response import build_response


def lambda_handler(event: dict, context) -> dict:
    user_id = event["pathParameters"]["id"]
    body = json.loads(event["body"])

    publisher = EventBridgePublisher(
        client=get_eventbridge_client(),
        event_bus_name=settings.EVENT_BUS_NAME,
    )
    publisher.publish("UserUpdated", {"userId": user_id, "data": body})

    return build_response(200, {"message": "Event sent"})
