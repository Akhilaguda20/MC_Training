import boto3
from datetime import datetime
from common.db import get_dynamodb, get_table_name
from common.response import build_response

dynamodb = get_dynamodb()
table_name = get_table_name()


def lambda_handler(event, context):
    try:
        detail = event["detail"]
        user_id = detail["userId"]

        dynamodb.update_item(
            TableName=table_name,
            Key={"userId": {"S": user_id}},
            UpdateExpression="SET #s = :s, processedAt = :t",
            ExpressionAttributeNames={
                "#s": "status"
            },
            ExpressionAttributeValues={
                ":s": {"S": "UPDATED"},
                ":t": {"S": datetime.utcnow().isoformat()}
            }
        )

        return {"statusCode": 200}

    except Exception as e:
        return {"statusCode": 500, "error": str(e)}