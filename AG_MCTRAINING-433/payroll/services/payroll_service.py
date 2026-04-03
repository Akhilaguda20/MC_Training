import uuid
from typing import Optional

from payroll.repositories.base import PayrollRepository


class PayrollService:
    """
    Business logic for the payroll domain.

    Has zero knowledge of DynamoDB, boto3, or HTTP.
    Receives the repository via constructor — fully testable with
    any implementation (real or fake) without patching.
    """

    def __init__(self, repo: PayrollRepository) -> None:
        self._repo = repo

    def create_payroll(self, data: dict) -> str:
        payroll_id = data.get("payrollId") or str(uuid.uuid4())
        self._repo.create(payroll_id, data)
        return payroll_id

    def get_payroll(self, payroll_id: str) -> Optional[dict]:
        return self._repo.get(payroll_id)

    def list_all_payrolls(self) -> list[dict]:
        return self._repo.list_all()

    def list_payroll_by_user(self, user_id: str) -> list[dict]:
        return self._repo.list_by_user(user_id)

    def update_payroll(self, payroll_id: str, data: dict) -> bool:
        return self._repo.update(payroll_id, data)

    def delete_payroll(self, payroll_id: str) -> None:
        self._repo.delete(payroll_id)
