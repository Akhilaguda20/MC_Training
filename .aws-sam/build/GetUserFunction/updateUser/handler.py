import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):

    try:
        path_params = event.get("pathParameters")

        if not path_params or "id" not in path_params:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "User ID missing"})
            }

        user_id = path_params["id"]
        body = json.loads(event.get("body") or "{}")

        name = body.get("name")
        email = body.get("email")

        if not name and not email:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Nothing to update"})
            }

        update_expression = []
        expression_values = {}

        if name:
            update_expression.append("name = :name")
            expression_values[":name"] = name

        if email:
            update_expression.append("email = :email")
            expression_values[":email"] = email

        table.update_item(
            Key={"userId": user_id},
            UpdateExpression="SET " + ", ".join(update_expression),
            ExpressionAttributeValues=expression_values
        )

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "User updated"})
        }

    except Exception as e:
        print("ERROR:", str(e))

        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Internal server error"})
        }