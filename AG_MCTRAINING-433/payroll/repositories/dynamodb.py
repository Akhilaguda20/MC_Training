import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class DynamoDBPayrollRepository:
    """
    The ONLY place in the codebase that knows about:
    - DynamoDB wire format  {"payrollId": {"S": "..."}}
    - UpdateExpression syntax
    - boto3 API method names (put_item, get_item, …)

    Client and table_name are injected via constructor — never created
    inside this class — so tests can pass in a MagicMock with zero patching.

    Table design
    ─────────────
    PK  payrollId  (S)   — globally unique record identifier
    GSI userId-index     — allows listing all payroll records for a user
    """

    def __init__(self, client, table_name: str) -> None:
        self._client = client
        self._table = table_name

    def create(self, payroll_id: str, data: dict) -> None:
        logger.info("DynamoDB put_item table=%s payroll_id=%s", self._table, payroll_id)
        self._client.put_item(
            TableName=self._table,
            Item={
                "payrollId":     {"S": payroll_id},
                "userId":        {"S": data.get("userId", "")},
                "baseSalary":    {"N": str(data.get("baseSalary", "0"))},
                "bonus":         {"N": str(data.get("bonus", "0"))},
                "deductions":    {"N": str(data.get("deductions", "0"))},
                "currency":      {"S": data.get("currency", "USD")},
                "effectiveDate": {"S": data.get("effectiveDate", "")},
                "status":        {"S": "ACTIVE"},
                "createdAt":     {"S": datetime.utcnow().isoformat()},
            },
        )
        logger.info("DynamoDB put_item succeeded table=%s payroll_id=%s", self._table, payroll_id)

    def get(self, payroll_id: str) -> Optional[dict]:
        logger.debug("DynamoDB get_item table=%s payroll_id=%s", self._table, payroll_id)
        response = self._client.get_item(
            TableName=self._table,
            Key={"payrollId": {"S": payroll_id}},
        )
        item = response.get("Item")
        if not item:
            logger.info("DynamoDB get_item not found table=%s payroll_id=%s", self._table, payroll_id)
            return None
        return self._flatten(item)

    def list_all(self) -> list[dict]:
        logger.debug("DynamoDB scan table=%s", self._table)
        response = self._client.scan(TableName=self._table)
        items = [self._flatten(item) for item in response.get("Items", [])]
        logger.info("DynamoDB scan returned %d items table=%s", len(items), self._table)
        return items

    def list_by_user(self, user_id: str) -> list[dict]:
        """
        Query the userId GSI to retrieve all salary records for a user.
        The GSI must be named 'userId-index' and project all attributes.
        """
        logger.debug("DynamoDB query userId-index table=%s user_id=%s", self._table, user_id)
        response = self._client.query(
            TableName=self._table,
            IndexName="userId-index",
            KeyConditionExpression="userId = :uid",
            ExpressionAttributeValues={":uid": {"S": user_id}},
        )
        items = [self._flatten(item) for item in response.get("Items", [])]
        logger.info("DynamoDB query returned %d items table=%s user_id=%s", len(items), self._table, user_id)
        return items

    def update(self, payroll_id: str, data: dict) -> bool:
        """
        Applies a partial update. Returns True if the item existed, False otherwise.
        Only fields present in `data` are updated.
        """
        # Build dynamic SET expression from the data dict
        set_parts: list[str] = ["updatedAt = :ua"]
        expr_names: dict = {}
        expr_values: dict = {":ua": {"S": datetime.utcnow().isoformat()}}

        field_map = {
            "baseSalary":    ("N", "baseSalary"),
            "bonus":         ("N", "bonus"),
            "deductions":    ("N", "deductions"),
            "currency":      ("S", "currency"),
            "effectiveDate": ("S", "effectiveDate"),
        }

        for field, (dtype, attr) in field_map.items():
            if field in data and data[field] is not None:
                placeholder = f":f_{field}"
                name_token = f"#n_{field}"
                expr_names[name_token] = attr
                set_parts.append(f"{name_token} = {placeholder}")
                expr_values[placeholder] = {dtype: str(data[field])}

        update_expression = "SET " + ", ".join(set_parts)

        kwargs = dict(
            TableName=self._table,
            Key={"payrollId": {"S": payroll_id}},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expr_values,
            ConditionExpression="attribute_exists(payrollId)",
            ReturnValues="NONE",
        )
        if expr_names:
            kwargs["ExpressionAttributeNames"] = expr_names

        logger.info("DynamoDB update_item table=%s payroll_id=%s", self._table, payroll_id)
        try:
            self._client.update_item(**kwargs)
            logger.info("DynamoDB update_item succeeded table=%s payroll_id=%s", self._table, payroll_id)
            return True
        except self._client.exceptions.ConditionalCheckFailedException:
            logger.warning("DynamoDB update_item not found table=%s payroll_id=%s", self._table, payroll_id)
            return False

    def delete(self, payroll_id: str) -> None:
        logger.info("DynamoDB delete_item table=%s payroll_id=%s", self._table, payroll_id)
        self._client.delete_item(
            TableName=self._table,
            Key={"payrollId": {"S": payroll_id}},
        )
        logger.info("DynamoDB delete_item succeeded table=%s payroll_id=%s", self._table, payroll_id)

    # ------------------------------------------------------------------ #

    @staticmethod
    def _flatten(item: dict) -> dict:
        """Collapse DynamoDB typed values → plain Python values."""
        result = {}
        for key, typed_val in item.items():
            dtype, value = next(iter(typed_val.items()))
            if dtype == "N":
                result[key] = value  # keep as string; callers can cast if needed
            else:
                result[key] = value
        return result
