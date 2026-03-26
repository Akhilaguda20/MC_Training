import boto3
import os

_TABLE_NAME = os.environ["TABLE_NAME"]
_dynamodb = boto3.client("dynamodb")


def get_dynamodb():
    return _dynamodb


def get_table_name():
    return _TABLE_NAME