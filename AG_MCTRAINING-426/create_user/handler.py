import json
import uuid
from botocore.exceptions import ClientError

from create_user.db import get_table
from create_user.response import build_response

def lambda_handler(event, context):
    try:
        payload = json.loads(event.get("body") or "{}")

        user_id = payload.get("id") or str(uuid.uuid4())
        name = payload.get("name")
        email = payload.get("email")

        if not name or not email:
            return build_response(400, {"message": "name and email are required"})

        item = {
            "id": user_id,
            "name": name,
            "email": email,
        }

        table = get_table()
        table.put_item(
            Item=item,
            ConditionExpression="attribute_not_exists(id)",
        )

        return build_response(201, item)

    except ClientError as e:
        code = e.response.get("Error", {}).get("Code")
        if code == "ConditionalCheckFailedException":
            return build_response(409, {"message": "User already exists"})
        return build_response(500, {"message": "Internal server error"})
    except Exception:
        return build_response(500, {"message": "Internal server error"})