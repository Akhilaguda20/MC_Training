from typing import Optional, Protocol, runtime_checkable


@runtime_checkable
class UserRepository(Protocol):
    """
    The contract for user data access.

    Any class that implements these four methods satisfies this protocol,
    including test fakes, without needing to inherit from this class.
    """

    def create(self, user_id: str, data: dict) -> None: ...

    def get(self, user_id: str) -> Optional[dict]: ...

    def update(self, user_id: str, data: Optional[dict] = None) -> None: ...

    def delete(self, user_id: str) -> None: ...
