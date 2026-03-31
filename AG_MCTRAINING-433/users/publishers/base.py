from typing import Protocol


class EventPublisher(Protocol):
    """
    Contract for event publishing.
    Service layer codes against this — never against EventBridge directly.
    """

    def publish(self, detail_type: str, detail: dict) -> None: ...
