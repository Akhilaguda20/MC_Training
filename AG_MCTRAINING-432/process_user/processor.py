from datetime import datetime
from common.db import get_dynamodb, get_table_name

dynamodb = get_dynamodb()
table_name = get_table_name()

def process_user_update(user_id: str, data: dict = None):
    dynamodb.update_item(
        TableName=table_name,
        Key={"userId": {"S": user_id}},
        UpdateExpression="SET #s = :s, processedAt = :t, lastModifiedBy = :m",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={
            ":s": {"S": "UPDATED"},
            ":t": {"S": datetime.utcnow().isoformat()},
            ":m": {"S": data.get("updatedBy", "system") if data else "system"}
        }
    )  

def process_user_create(user_id: str, data: dict):
    
    dynamodb.put_item(
        TableName=table_name,
        Item={
            "userId":    {"S": user_id},
            "name":      {"S": data.get("name", "")},
            "email":     {"S": data.get("email", "")},
            "status":    {"S": "CREATED"},
            "createdAt": {"S": datetime.utcnow().isoformat()}
        }
    )

def process_user_delete(user_id: str):
    dynamodb.delete_item(
        TableName=table_name,
        Key={"userId": {"S": user_id}}
    )

def process_user_get(user_id: str):
    response = dynamodb.get_item(
        TableName=table_name,
        Key={"userId": {"S": user_id}}
    )
    item = response.get("Item")
    if not item:
        return None
    # Flatten DynamoDB format {"userId": {"S": "..."}} → {"userId": "..."}
    return {k: list(v.values())[0] for k, v in item.items()}