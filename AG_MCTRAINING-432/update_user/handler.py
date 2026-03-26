import json, boto3, os

eventbridge = boto3.client("events", endpoint_url=os.environ.get("LOCALSTACK_URL"), region_name="us-east-1")

def lambda_handler(event, context):
    user_id = event["pathParameters"]["id"]
    body = json.loads(event["body"])
    eventbridge.put_events(Entries=[{
        "Source": "user.service",
        "DetailType": "UserUpdated",
        "Detail": json.dumps({"userId": user_id, "data": body}),
        "EventBusName": os.environ["EVENT_BUS_NAME"]
    }])
    return {"statusCode": 200, "body": json.dumps({"message": "Event sent"})}