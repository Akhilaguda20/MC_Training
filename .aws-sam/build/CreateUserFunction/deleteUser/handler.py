import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):

    try:
        user_id = event['pathParameters']['id']

        table.delete_item(
            Key={"userId": user_id}
        )

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "User deleted"})
        }

    except Exception as e:
        print(str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Internal server error"})
        }