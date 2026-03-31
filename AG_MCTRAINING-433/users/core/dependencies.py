from users.core.config import settings
from users.db.session import get_dynamodb_client, get_eventbridge_client
from users.publishers.eventbridge import EventBridgePublisher
from users.repositories.dynamodb import DynamoDBUserRepository
from users.services.user_service import UserService


def get_user_service() -> UserService:
    """
    FastAPI dependency factory — wires the full object graph together.

    Called once per request (not at import time), so:
    - boto3 clients are only created when a real request arrives
    - Tests override this with app.dependency_overrides[get_user_service]
      and inject fakes — no patching needed anywhere else
    """
    repo = DynamoDBUserRepository(
        client=get_dynamodb_client(),
        table_name=settings.TABLE_NAME,
    )
    publisher = EventBridgePublisher(
        client=get_eventbridge_client(),
        event_bus_name=settings.EVENT_BUS_NAME,
    )
    return UserService(repo, publisher)