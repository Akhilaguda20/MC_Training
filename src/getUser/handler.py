import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):

    try:
        user_id = event['pathParameters']['id']

        response = table.get_item(
            Key={"userId": user_id}
        )

        if "Item" not in response:
            return {
                "statusCode": 404,
                "body": json.dumps({"message": "User not found"})
            }

        return {
            "statusCode": 200,
            "body": json.dumps(response["Item"])
        }

    except Exception as e:
        print(str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Internal server error"})
        }