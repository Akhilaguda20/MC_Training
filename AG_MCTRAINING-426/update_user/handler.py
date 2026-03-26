import json
from botocore.exceptions import ClientError

from update_user.db import get_table
from update_user.response import build_response

def lambda_handler(event, context):
    try:
        payload = json.loads(event.get("body") or "{}")
        path_params = event.get("pathParameters") or {}
        query_params = event.get("queryStringParameters") or {}

        user_id = path_params.get("id") or query_params.get("id") or payload.get("id")
        name = payload.get("name")
        email = payload.get("email")

        if not user_id:
            return build_response(400, {"message": "id is required"})

        updates = {}
        if name is not None:
            updates["name"] = name
        if email is not None:
            updates["email"] = email

        if not updates:
            return build_response(400, {"message": "At least one of name or email is required"})

        update_parts = []
        expr_attr_names = {}
        expr_attr_values = {}

        for field, value in updates.items():
            name_token = f"#{field}"
            value_token = f":{field}"
            update_parts.append(f"{name_token} = {value_token}")
            expr_attr_names[name_token] = field
            expr_attr_values[value_token] = value

        table = get_table()
        result = table.update_item(
            Key={"id": user_id},
            UpdateExpression="SET " + ", ".join(update_parts),
            ExpressionAttributeNames=expr_attr_names,
            ExpressionAttributeValues=expr_attr_values,
            ConditionExpression="attribute_exists(id)",
            ReturnValues="ALL_NEW",
        )

        return build_response(200, result.get("Attributes", {}))

    except ClientError as e:
        code = e.response.get("Error", {}).get("Code")
        if code == "ConditionalCheckFailedException":
            return build_response(404, {"message": "User not found"})
        return build_response(500, {"message": "Internal server error"})
    except Exception:
        return build_response(500, {"message": "Internal server error"})