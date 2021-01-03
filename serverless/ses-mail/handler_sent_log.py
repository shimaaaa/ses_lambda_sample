import base64
import json
import logging
import os
from datetime import datetime

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.resource("s3")
s3_bucket = os.environ["LOG_S3_BUCKET"]


def _get_send_date_str(send_datetime_str: str) -> str:
    send_datetime_str = send_datetime_str.replace("Z", "+00:00")  # trim Z
    send_datetime = datetime.fromisoformat(send_datetime_str)
    send_date_str = send_datetime.strftime("%Y-%m-%d")
    return send_date_str


def lambda_handler(event, context):
    message = json.loads(event["Records"][0]["Sns"]["Message"])
    message_id = message["mail"]["messageId"]
    event_type = message["eventType"]

    send_datetime_str = message["mail"]["timestamp"]
    send_date_str = _get_send_date_str(send_datetime_str)

    if event_type == "Click":
        click_link = message["click"]["link"]
        click_link_b64 = base64.b64encode(click_link.encode()).decode()
        filename = f"{event_type}_{click_link_b64}.json"
    else:
        filename = f"{event_type}.json"

    key = f"ses_message/logs/payloads/date={send_date_str}/message_id={message_id}/{filename}"
    file_contents = json.dumps(message)

    obj = s3.Object(s3_bucket, key)
    obj.put(Body=file_contents)
