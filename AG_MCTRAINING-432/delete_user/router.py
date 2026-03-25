import json
import boto3
import os
from fastapi import APIRouter
from process_user.processor import process_user_delete

EVENT_BUS_NAME = os.environ["EVENT_BUS_NAME"]
LOCALSTACK_URL = os.environ.get("LOCALSTACK_URL")

eventbridge = boto3.client("events", endpoint_url=LOCALSTACK_URL, region_name="us-east-1")

router = APIRouter()

@router.delete("/user/{id}")
async def delete_user(id: str):
    eventbridge.put_events(
        Entries=[
            {
                "Source": "user.service",
                "DetailType": "UserDeleted",
                "Detail": json.dumps({"userId": id}),
                "EventBusName": EVENT_BUS_NAME
            }
        ]
    )
    process_user_delete(id)
    return {"message": "User deleted"}