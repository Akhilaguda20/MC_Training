import boto3
import os
from fastapi import APIRouter, HTTPException
from process_user.processor import process_user_get

router = APIRouter()

@router.get("/user/{id}")
async def get_user(id: str):
    user = process_user_get(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user