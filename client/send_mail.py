import argparse
import json
import uuid

import boto3

S3_BUCKET = "seslogtest"
BODY_HTML = """
<html>
<head></head>
<body>
  <h1>Amazon SES Test (SDK for Python)</h1>
  <p>This email was sent with
    <a href='https://aws.amazon.com/ses/'>Amazon SES</a> using the
    <a href='https://aws.amazon.com/sdk-for-python/'>
      AWS SDK for Python (Boto)</a>.</p>
</body>
</html>
"""


def _upload_body(message_key):
    s3 = boto3.resource("s3")
    key = f"ses_message/body/{message_key}.html"
    obj = s3.Object(S3_BUCKET, key)
    obj.put(Body=BODY_HTML)
    return key


def _send_sqs_message(recipient, sender, body_object_key):
    client = boto3.client("sqs")
    queue_url_response = client.get_queue_url(
        QueueName="ses_send_mail",
    )
    message_subject = "MAIL TEST"
    message_body = {
        "message_recipient": [recipient],
        "message_subject": message_subject,
        "message_sender": f"Sender Name <sender@snmtest10.xyz>",
        "ses_tags": [{"Name": "campaignId", "Value": "test01"}],
        "ses_configration_set": "ses_log",
        "html_template_s3_key": body_object_key,
        "text_template_s3_key": None,
        "html_context": {
            "test": "hello"
        }
    }
    response = client.send_message(
        QueueUrl=queue_url_response["QueueUrl"],
        MessageBody=json.dumps(message_body),
    )
    print(response)


def _argparse():
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--recipient")
    parser.add_argument("-s", "--sender")
    return parser.parse_args()


def main():
    args = _argparse()
    message_key = str(uuid.uuid4())
    body_object_key = _upload_body(message_key)
    _send_sqs_message(
        recipient=args.recipient, sender=args.sender, body_object_key=body_object_key
    )


if __name__ == "__main__":
    main()
