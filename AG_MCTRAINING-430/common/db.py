import boto3
import os

_TABLE_NAME = os.environ["TABLE_NAME"]
_LOCALSTACK_URL = os.environ.get("LOCALSTACK_URL")

_dynamodb = boto3.client(
    "dynamodb",
    endpoint_url=_LOCALSTACK_URL,
    region_name="us-east-1"
)

def get_dynamodb():
    return _dynamodb

def get_table_name():
    return _TABLE_NAME