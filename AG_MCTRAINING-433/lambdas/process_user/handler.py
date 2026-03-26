"""
Lambda handler — triggered by SQS.

SQS receives EventBridge events forwarded from the "user-events-bus".
Each record body contains an EventBridge envelope:

    {
        "detail-type": "UserUpdated",
        "detail": {
            "userId": "abc-123",
            "data": { "updatedBy": "admin" }
        }
    }

This handler is responsible for applying the update to DynamoDB directly,
keeping the write path decoupled from the HTTP API.
"""

import json
import os
import sys

# Ensure bundled dependencies are importable in Lambda
if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):  # pragma: no cover
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "dependencies"))

from users.core.config import settings
from users.db.session import get_dynamodb_client
from users.repositories.dynamodb import DynamoDBUserRepository


def lambda_handler(event: dict, context) -> None:
    repo = DynamoDBUserRepository(
        client=get_dynamodb_client(),
        table_name=settings.TABLE_NAME,
    )

    for record in event["Records"]:
        eb_event = json.loads(record["body"])
        detail = eb_event.get("detail", {})
        user_id = detail["userId"]
        data = detail.get("data", {})
        repo.update(user_id, data)
