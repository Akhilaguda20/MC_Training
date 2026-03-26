import json
import boto3
import os
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

EVENT_BUS_NAME = os.environ["EVENT_BUS_NAME"]
LOCALSTACK_URL = os.environ.get("LOCALSTACK_URL")

eventbridge = boto3.client("events", endpoint_url=LOCALSTACK_URL, region_name="us-east-1")

router = APIRouter()

class UserUpdateBody(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None

@router.put("/user/{id}")
async def update_user(id: str, body: UserUpdateBody):
    eventbridge.put_events(
        Entries=[
            {
                "Source": "user.service",
                "DetailType": "UserUpdated",
                "Detail": json.dumps({"userId": id, "data": body.model_dump()}),
                "EventBusName": EVENT_BUS_NAME
            }
        ]
    )
    return {"message": "Event sent"}