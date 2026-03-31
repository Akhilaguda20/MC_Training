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
        except KeyError as exc:
            logger.exception("Malformed event — missing key %s; body=%s", exc, record["body"])
            raise
        except Exception:
            logger.exception("Unexpected error processing record; body=%s", record["body"])
            raise
