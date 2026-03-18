import os
import boto3

_dynamodb = boto3.resource("dynamodb")
_table = None


def get_table():
    global _table
    if _table is None:
        table_name = os.environ["TABLE_NAME"]
        _table = _dynamodb.Table(table_name)
    return _table