"""
Lambda handler — triggered by SQS (PayrollUserCreatedQueue).

SQS receives EventBridge events from the "user-events-bus" filtered on
detail-type "UserCreated".  Each record body is an EventBridge envelope:

    {
        "detail-type": "UserCreated",
        "detail": {
            "userId": "abc-123",
            "data": {
                "name": "Alice",
                "email": "alice@example.com",
                ...
            }
        }
    }

This handler creates an initial payroll record in the PayrollTable for
the newly created user, keeping the write path decoupled from the HTTP API.
"""

import json
import logging

from payroll.core.config import settings
from payroll.db.session import get_dynamodb_client
from payroll.repositories.dynamodb import DynamoDBPayrollRepository
from payroll.services.payroll_service import PayrollService

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _log(level: str, event: str, **kwargs) -> None:
    logger.log(
        getattr(logging, level),
        json.dumps({"event": event, **kwargs}),
    )


def lambda_handler(event: dict, context) -> None:
    repo = DynamoDBPayrollRepository(
        client=get_dynamodb_client(),
        table_name=settings.PAYROLL_TABLE_NAME,
    )
    service = PayrollService(repo)

    for record in event["Records"]:
        try:
            eb_event = json.loads(record["body"])
            detail = eb_event.get("detail", {})
            user_id = detail["userId"]

            service.create_payroll(
                {
                    "userId": user_id,
                    "baseSalary": "0",
                    "bonus": "0",
                    "deductions": "0",
                    "currency": "USD",
                    "effectiveDate": "",
                }
            )
            _log("INFO", "payroll_created", user_id=user_id)
        except KeyError as exc:
            _log("ERROR", "malformed_event", missing_key=str(exc), body=record["body"])
            raise
        except Exception as exc:
            _log("ERROR", "unexpected_error", error=str(exc), body=record["body"])
            raise
