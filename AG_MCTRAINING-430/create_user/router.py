import json
import boto3
import os
import uuid
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from process_user.processor import process_user_create

EVENT_BUS_NAME = os.environ["EVENT_BUS_NAME"]
LOCALSTACK_URL = os.environ.get("LOCALSTACK_URL")

eventbridge = boto3.client("events", endpoint_url=LOCALSTACK_URL, region_name="us-east-1")

router = APIRouter()

class UserCreateBody(BaseModel):
    userId: Optional[str] = None 
    name: str
    email: str

@router.post("/user", status_code=201)
async def create_user(body: UserCreateBody):
    user_id = body.userId or str(uuid.uuid4())   # use provided or generate

    eventbridge.put_events(
        Entries=[
            {
                "Source": "user.service",
                "DetailType": "UserCreated",
                "Detail": json.dumps({"userId": user_id, "data": body.model_dump()}),
                "EventBusName": EVENT_BUS_NAME
            }
        ]
    )
    process_user_create(user_id, body.model_dump())
    return {"message": "User created", "userId": user_id}