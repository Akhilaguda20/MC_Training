import uuid
from typing import Optional

from users.publishers.base import EventPublisher
from users.repositories.base import UserRepository


class UserService:
    """
    Business logic for the user domain.

    Has zero knowledge of DynamoDB, EventBridge, boto3, or HTTP.
    Receives both dependencies via constructor — fully testable with
    any implementation (real or fake) without patching.
    """

    def __init__(self, repo: UserRepository, publisher: EventPublisher) -> None:
        self._repo = repo
        self._publisher = publisher

    def create_user(self, data: dict) -> str:
        user_id = data.get("userId") or str(uuid.uuid4())
        self._repo.create(user_id, data)
        self._publisher.publish("UserCreated", {"userId": user_id, "data": data})
        return user_id

    def get_user(self, user_id: str) -> Optional[dict]:
        return self._repo.get(user_id)

    def update_user(self, user_id: str, data: dict) -> None:
        # Publishes event only — a downstream Lambda (process_user) applies
        # the update to DynamoDB after consuming the event from the queue.
        self._publisher.publish("UserUpdated", {"userId": user_id, "data": data})

    def delete_user(self, user_id: str) -> None:
        self._publisher.publish("UserDeleted", {"userId": user_id})
        self._repo.delete(user_id)
