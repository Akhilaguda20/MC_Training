from typing import Optional, Protocol, runtime_checkable


@runtime_checkable
class PayrollRepository(Protocol):
    """
    The contract for payroll data access.

    Any class that implements these methods satisfies this protocol,
    including test fakes, without needing to inherit from this class.
    """

    def create(self, payroll_id: str, data: dict) -> None: ...

    def get(self, payroll_id: str) -> Optional[dict]: ...

    def list_all(self) -> list[dict]: ...

    def list_by_user(self, user_id: str) -> list[dict]: ...

    def update(self, payroll_id: str, data: dict) -> bool: ...

    def delete(self, payroll_id: str) -> None: ...
