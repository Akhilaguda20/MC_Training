"""
conftest.py — shared fixtures for all payroll tests.

Environment variables are set HERE, before any app module is imported.
Because payroll/core/config.py uses @property (reads os.environ on each access),
setting them here is sufficient — no global patching of boto3 needed.
"""

import os
from typing import Optional

import pytest

os.environ.setdefault("PAYROLL_TABLE_NAME", "test-payroll-table")


class InMemoryPayrollRepository:
    """A dict-backed PayrollRepository — no boto3, no DynamoDB, no mocking."""

    def __init__(self):
        self._store: dict = {}

    def create(self, payroll_id: str, data: dict) -> None:
        self._store[payroll_id] = {
            "payrollId": payroll_id,
            "userId": data.get("userId", ""),
            "baseSalary": str(data.get("baseSalary", "0")),
            "bonus": str(data.get("bonus", "0")),
            "deductions": str(data.get("deductions", "0")),
            "currency": data.get("currency", "USD"),
            "effectiveDate": data.get("effectiveDate", ""),
            "status": "ACTIVE",
        }

    def get(self, payroll_id: str) -> Optional[dict]:
        return self._store.get(payroll_id)

    def list_all(self) -> list[dict]:
        return list(self._store.values())

    def list_by_user(self, user_id: str) -> list[dict]:
        return [r for r in self._store.values() if r.get("userId") == user_id]

    def update(self, payroll_id: str, data: dict) -> bool:
        if payroll_id not in self._store:
            return False
        for field in ("baseSalary", "bonus", "deductions", "currency", "effectiveDate"):
            if field in data and data[field] is not None:
                self._store[payroll_id][field] = str(data[field])
        return True

    def delete(self, payroll_id: str) -> None:
        self._store.pop(payroll_id, None)


# --------------------------------------------------------------------------- #
# Pytest fixtures                                                              #
# --------------------------------------------------------------------------- #

@pytest.fixture
def fake_repo():
    return InMemoryPayrollRepository()
