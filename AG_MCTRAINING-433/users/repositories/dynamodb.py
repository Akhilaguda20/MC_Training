from datetime import datetime
from typing import Optional


class DynamoDBUserRepository:
    """
    The ONLY place in the codebase that knows about:
    - DynamoDB wire format  {"userId": {"S": "..."}}
    - UpdateExpression syntax
    - boto3 API method names (put_item, get_item, …)

    Client and table_name are injected via constructor — never created
    inside this class — so tests can pass in a MagicMock with zero patching.
    """

    def __init__(self, client, table_name: str) -> None:
        self._client = client
        self._table = table_name

    def create(self, user_id: str, data: dict) -> None:
        self._client.put_item(
            TableName=self._table,
            Item={
                "userId":    {"S": user_id},
                "name":      {"S": data.get("name", "")},
                "email":     {"S": data.get("email", "")},
                "status":    {"S": "CREATED"},
                "createdAt": {"S": datetime.utcnow().isoformat()},
            },
        )

    def get(self, user_id: str) -> Optional[dict]:
        response = self._client.get_item(
            TableName=self._table,
            Key={"userId": {"S": user_id}},
        )
        item = response.get("Item")
        if not item:
            return None
        # Flatten DynamoDB format {"userId": {"S": "..."}} → {"userId": "..."}
        return {k: list(v.values())[0] for k, v in item.items()}

    def update(self, user_id: str, data: Optional[dict] = None) -> None:
        self._client.update_item(
            TableName=self._table,
            Key={"userId": {"S": user_id}},
            UpdateExpression="SET #s = :s, processedAt = :t, lastModifiedBy = :m",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={
                ":s": {"S": "UPDATED"},
                ":t": {"S": datetime.utcnow().isoformat()},
                ":m": {"S": data.get("updatedBy", "system") if data else "system"},
            },
        )

    def delete(self, user_id: str) -> None:
        self._client.delete_item(
            TableName=self._table,
            Key={"userId": {"S": user_id}},
        )
