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
import logging

from users.core.config import settings
from users.db.session import get_dynamodb_client
from users.repositories.dynamodb import DynamoDBUserRepository

logger = logging.getLogger(__name__)


def lambda_handler(event: dict, context) -> None:
    repo = DynamoDBUserRepository(
        client=get_dynamodb_client(),
        table_name=settings.TABLE_NAME,
    )

    for record in event["Records"]:
        try:
            eb_event = json.loads(record["body"])
            detail = eb_event.get("detail", {})
            user_id = detail["userId"]
            data = detail.get("data", {})
            repo.update(user_id, data)
        except KeyError as exc:
            logger.exception("Malformed event — missing key %s; body=%s", exc, record["body"])
            raise
        except Exception:
            logger.exception("Unexpected error processing record; body=%s", record["body"])
            raise
