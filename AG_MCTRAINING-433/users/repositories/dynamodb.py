import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


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
        logger.info("DynamoDB put_item table=%s user_id=%s", self._table, user_id)
        self._client.put_item(
            TableName=self._table,
            Item={
                "userId":    {"S": user_id},
                "name":      {"S": data.get("name", "")},
                "email":     {"S": data.get("email", "")},
                "status":    {"S": "CREATED"},
                "createdAt": {"S": datetime.utcnow().isoformat()},
            },
            ConditionExpression="attribute_not_exists(userId)",
        )
        logger.info("DynamoDB put_item succeeded table=%s user_id=%s", self._table, user_id)

    def get(self, user_id: str) -> Optional[dict]:
        logger.debug("DynamoDB get_item table=%s user_id=%s", self._table, user_id)
        response = self._client.get_item(
            TableName=self._table,
            Key={"userId": {"S": user_id}},
        )
        item = response.get("Item")
        if not item:
            logger.info("DynamoDB get_item not found table=%s user_id=%s", self._table, user_id)
            return None
        # Flatten DynamoDB format {"userId": {"S": "..."}} → {"userId": "..."}
        return {k: list(v.values())[0] for k, v in item.items()}

    def list_all(self) -> list[dict]:
        logger.debug("DynamoDB scan table=%s", self._table)
        items = []
        kwargs: dict = {"TableName": self._table}
        while True:
            response = self._client.scan(**kwargs)
            items.extend(
                [{k: list(v.values())[0] for k, v in item.items()} for item in response.get("Items", [])]
            )
            last_key = response.get("LastEvaluatedKey")
            if not last_key:
                break
            kwargs["ExclusiveStartKey"] = last_key
        logger.info("DynamoDB scan returned %d items table=%s", len(items), self._table)
        return items

    def update(self, user_id: str, data: Optional[dict] = None) -> None:
        data = data or {}
        expression_parts = ["#s = :s", "processedAt = :t", "lastModifiedBy = :m"]
        attr_names = {"#s": "status"}
        attr_values = {
            ":s": {"S": "UPDATED"},
            ":t": {"S": datetime.utcnow().isoformat()},
            ":m": {"S": data.get("updatedBy", "system")},
        }
        if "name" in data:
            expression_parts.append("#n = :n")
            attr_names["#n"] = "name"
            attr_values[":n"] = {"S": data["name"]}
        if "email" in data:
            expression_parts.append("email = :e")
            attr_values[":e"] = {"S": data["email"]}

        logger.info("DynamoDB update_item table=%s user_id=%s", self._table, user_id)
        self._client.update_item(
            TableName=self._table,
            Key={"userId": {"S": user_id}},
            UpdateExpression="SET " + ", ".join(expression_parts),
            ExpressionAttributeNames=attr_names,
            ExpressionAttributeValues=attr_values,
        )
        logger.info("DynamoDB update_item succeeded table=%s user_id=%s", self._table, user_id)

    def delete(self, user_id: str) -> None:
        logger.info("DynamoDB delete_item table=%s user_id=%s", self._table, user_id)
        self._client.delete_item(
            TableName=self._table,
            Key={"userId": {"S": user_id}},
        )
        logger.info("DynamoDB delete_item succeeded table=%s user_id=%s", self._table, user_id)
