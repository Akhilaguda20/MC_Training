import json
import boto3
from common.db import get_dynamodb, get_table_name
from common.response import build_response
eventbridge = boto3.client("events")


def lambda_handler(event, context):
    try:
        dynamodb = get_dynamodb()
        table_name = get_table_name()

        user_id = event["pathParameters"]["id"]
        body = json.loads(event.get("body", "{}"))

        name = body.get("name")
        email = body.get("email")

        update_expr = []
        expr_attr_values = {}
        expr_attr_names = {}

        if name:
            update_expr.append("#n = :n")
            expr_attr_names["#n"] = "name"
            expr_attr_values[":n"] = {"S": name}

        if email:
            update_expr.append("#e = :e")
            expr_attr_names["#e"] = "email"
            expr_attr_values[":e"] = {"S": email}

        if not update_expr:
            return build_response(400, {"message": "No fields to update"})

        dynamodb.update_item(
            TableName=table_name,
            Key={"userId": {"S": user_id}},
            UpdateExpression="SET " + ", ".join(update_expr),
            ExpressionAttributeNames=expr_attr_names,
            ExpressionAttributeValues=expr_attr_values
        )

        eventbridge.put_events(
            Entries=[
                {
                    "Source": "user.service",
                    "DetailType": "UserUpdated",
                    "Detail": json.dumps({"userId": user_id}),
                    "EventBusName": "default"
                }
            ]
        )

        return build_response(200, {"message": "User updated & event sent"})

    except Exception as e:
        return build_response(500, {"error": str(e)})