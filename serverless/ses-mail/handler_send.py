import json
import logging
import os
from typing import List, Optional

import boto3
import pydantic
from jinja2 import Template

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.resource("s3")
s3_bucket = os.environ["MESSAGE_BODY_S3_BUCKET"]
CHARSET = "UTF-8"
ses_region = os.environ["SES_REGION"]
ses = boto3.client("ses", region_name=ses_region)


def _get_s3_data(key: str) -> str:
    obj = s3.Object(s3_bucket, key)
    response = obj.get()
    body = response["Body"].read()
    return body.decode(CHARSET)


def _delete_s3_obj(key: str):
    obj = s3.Object(s3_bucket, key)
    obj.delete()


class SESMessage(pydantic.BaseModel):
    recipient: List[str]
    subject: str
    sender: str
    configration_set: Optional[str]
    tags: Optional[List[dict]]
    html_template_s3_key: str
    text_template_s3_key: Optional[str]
    html_context: dict = dict
    text_context: dict = dict

    @property
    def html_message(self) -> str:
        template_data = _get_s3_data(self.html_template_s3_key)
        template = Template(template_data)
        return template.render(self.html_context)

    @property
    def text_message(self) -> Optional[str]:
        if self.text_template_s3_key is None:
            return None
        template_data = _get_s3_data(self.text_template_s3_key)
        template = Template(template_data)
        return template.render(self.text_context)

    def send_mail_kwargs(self):
        kwargs = {
            "Destination": {"ToAddresses": self.recipient},
            "Message": {
                "Body": {
                    "Html": {
                        "Charset": CHARSET,
                        "Data": self.html_message,
                    }
                },
                "Subject": {
                    "Charset": CHARSET,
                    "Data": self.subject,
                },
            },
            "Source": self.sender,
            "Tags": self.tags,
            "ConfigurationSetName": self.configration_set,
        }
        if self.text_message is not None:
            kwargs["Message"]["Body"]["Text"] = {
                "Charset": CHARSET,
                "Data": self.text_message,
            }
        return kwargs


def _get_sqs_message(event) -> SESMessage:
    sqs_message = json.loads(event["Records"][0]["body"])
    logger.info(sqs_message)
    message_recipient = sqs_message.get("message_recipient")
    message_subject = sqs_message.get("message_subject")
    message_sender = sqs_message.get("message_sender")
    ses_tags = sqs_message.get("ses_tags")
    ses_configration_set = sqs_message.get("ses_configration_set")
    html_template_s3_key = sqs_message.get("html_template_s3_key")
    text_template_s3_key = sqs_message.get("text_template_s3_key")
    html_context = sqs_message.get("html_context")
    text_context = sqs_message.get("text_context")

    message = SESMessage(
        recipient=message_recipient,
        subject=message_subject,
        sender=message_sender,
        configration_set=ses_configration_set,
        tags=ses_tags,
        html_template_s3_key=html_template_s3_key,
        text_template_s3_key=text_template_s3_key,
        html_context=html_context,
        text_context=text_context,
    )
    return message


def lambda_handler(event, context):
    message = _get_sqs_message(event)
    ses.send_email(**message.send_mail_kwargs())
