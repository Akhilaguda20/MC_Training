from payroll.core.config import settings
from payroll.db.session import get_dynamodb_client
from payroll.repositories.dynamodb import DynamoDBPayrollRepository
from payroll.services.payroll_service import PayrollService


def get_payroll_service() -> PayrollService:
    """
    FastAPI dependency factory — wires the full object graph together.

    Called once per request (not at import time), so:
    - boto3 clients are only created when a real request arrives
    - Tests override this with app.dependency_overrides[get_payroll_service]
      and inject fakes — no patching needed anywhere else
    """
    repo = DynamoDBPayrollRepository(
        client=get_dynamodb_client(),
        table_name=settings.PAYROLL_TABLE_NAME,
    )
    return PayrollService(repo)
