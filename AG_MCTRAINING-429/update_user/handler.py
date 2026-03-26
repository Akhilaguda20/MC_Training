import json
import boto3
import os

eventbridge = boto3.client("events")

EVENT_BUS_NAME = os.environ["EVENT_BUS_NAME"]

def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}"))
    user_id = event["pathParameters"]["id"]

    # Example event send
    eventbridge.put_events(
        Entries=[
            {
                "Source": "user.service",
                "DetailType": "UserUpdated",
                "Detail": json.dumps({
                    "userId": user_id,
                    "data": body
                }),
                "EventBusName": EVENT_BUS_NAME   
            }
        ]
    )

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Event sent"})
    }