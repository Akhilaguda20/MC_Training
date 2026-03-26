import json


def build_response(status_code: int, body: dict) -> dict:
    """Builds a Lambda/API Gateway proxy response dict."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body),
    }
