import json
from datetime import datetime
from common.db import get_dynamodb, get_table_name

dynamodb = get_dynamodb()
table_name = get_table_name()

def lambda_handler(event, context):
    for record in event['Records']:
        body = json.loads(record['body'])
        detail = body["detail"]  # EventBridge event is wrapped in SQS
        user_id = detail["userId"]

        dynamodb.update_item(
            TableName=table_name,
            Key={"userId": {"S": user_id}},
            UpdateExpression="SET #s = :s, processedAt = :t",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={
                ":s": {"S": "UPDATED"},
                ":t": {"S": datetime.utcnow().isoformat()}
            }
        )