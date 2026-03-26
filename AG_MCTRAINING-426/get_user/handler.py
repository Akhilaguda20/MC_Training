import json
from botocore.exceptions import ClientError

from get_user.db import get_table
from get_user.response import build_response

def lambda_handler(event, context):
    try:
        payload = json.loads(event.get("body") or "{}")
        path_params = event.get("pathParameters") or {}
        query_params = event.get("queryStringParameters") or {}
        user_id = path_params.get("id") or query_params.get("id") or payload.get("id")

        if not user_id:
            return build_response(400, {"message": "id is required"})

        table = get_table()
        result = table.get_item(Key={"id": user_id})
        item = result.get("Item")

        if not item:
            return build_response(404, {"message": "User not found"})

        return build_response(200, item)

    except ClientError:
        return build_response(500, {"message": "Internal server error"})
    except Exception:
        return build_response(500, {"message": "Internal server error"})