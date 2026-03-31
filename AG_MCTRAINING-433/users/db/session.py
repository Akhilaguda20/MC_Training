import boto3

from users.core.config import settings


def get_dynamodb_client():
    """
    Factory function — called at request time, NOT at import time.
    This prevents module-level boto3.client() calls that break testing.
    """
    return boto3.client(
        "dynamodb",
        endpoint_url=settings.LOCALSTACK_URL,
        region_name=settings.AWS_REGION,
    )


def get_eventbridge_client():
    return boto3.client(
        "events",
        endpoint_url=settings.LOCALSTACK_URL,
        region_name=settings.AWS_REGION,
    )
