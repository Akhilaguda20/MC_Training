import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "dependencies"))
import json
from process_user.processor import process_user_update

def lambda_handler(event, context):
    for record in event["Records"]:
        # SQS body contains the EventBridge event as a string
        eb_event = json.loads(record["body"])
        detail = eb_event.get("detail", {})
        user_id = detail["userId"]
        data = detail.get("data", {})
        process_user_update(user_id, data)   # passes data so new field can use it