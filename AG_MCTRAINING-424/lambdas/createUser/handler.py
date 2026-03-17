import json
import boto3
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('users')

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])

        name = body.get("name")
        email = body.get("email")

        if not name or not email:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "name and email are required"})
            }

        user_id = str(uuid.uuid4())

        item = {
            "userId": user_id,
            "name": name,
            "email": email
        }

        table.put_item(Item=item)

        return {
            "statusCode": 201,
            "body": json.dumps({
                "message": "User created",
                "user": item
            })
        }

    except Exception as e:
        print(str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Internal server error"})
        }