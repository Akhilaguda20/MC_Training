"""
tests/test_dependencies.py

Covers: payroll/core/dependencies.py — get_payroll_service().
The factory is patched at the db-session level so no real boto3 calls are made.
"""

from payroll.core.dependencies import get_payroll_service
from payroll.services.payroll_service import PayrollService


class TestGetPayrollService:
    def test_returns_payroll_service_instance(self, mocker):
        mocker.patch(
            "payroll.core.dependencies.get_dynamodb_client",
            return_value=mocker.MagicMock(),
        )

        service = get_payroll_service()

        assert isinstance(service, PayrollService)
