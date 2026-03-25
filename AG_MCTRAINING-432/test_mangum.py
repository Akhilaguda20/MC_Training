import json
import os

# Set env vars before importing main (mimics Lambda environment)
os.environ["TABLE_NAME"] = "users_events"
os.environ["EVENT_BUS_NAME"] = "user-events-bus"
os.environ["LOCALSTACK_URL"] = "http://localhost:4566"

from main import handler  # Mangum handler

def make_event(method, path, body=None, path_params=None):
    return {
        "resource": path,                          # <-- was missing
        "httpMethod": method,
        "path": path,
        "headers": {"content-type": "application/json"},
        "multiValueHeaders": {},
        "queryStringParameters": None,
        "multiValueQueryStringParameters": None,
        "pathParameters": path_params,
        "stageVariables": None,
        "body": json.dumps(body) if body else None,
        "requestContext": {
            "resourceId": "test",
            "resourcePath": path,                  # <-- was missing
            "httpMethod": method,                  # <-- was missing
            "stage": "local",                      # <-- was missing
            "requestId": "test-local",
            "identity": {"sourceIp": "127.0.0.1"},
            "apiId": "test-api"                    # <-- was missing
        },
        "isBase64Encoded": False
    }
# --- CREATE USER ---
print("=== POST /user ===")
event = make_event("POST", "/user", {"name": "Alice", "email": "alice@example.com"})
response = handler(event, {})
print(response)
body = json.loads(response["body"])
user_id = body.get("userId")

# --- GET USER ---
print("\n=== GET /user/{id} ===")
event = make_event("GET", f"/user/{user_id}", path_params={"id": user_id})
response = handler(event, {})
print(response)

# --- UPDATE USER ---
print("\n=== PUT /user/{id} ===")
event = make_event("PUT", f"/user/{user_id}", {"name": "Alice Updated"}, path_params={"id": user_id})
response = handler(event, {})
print(response)

# --- DELETE USER ---
print("\n=== DELETE /user/{id} ===")
event = make_event("DELETE", f"/user/{user_id}", path_params={"id": user_id})
response = handler(event, {})
print(response)