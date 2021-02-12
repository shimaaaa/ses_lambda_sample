import base64
import json
import logging
import pathlib

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def _add_column(ses_event):
    ses_event["mail_timestamp"] = ses_event["mail"]["timestamp"]
    ses_event["mail_destination"] = ses_event["mail"]["destination"]
    ses_event["mail_message_id"] = ses_event["mail"]["messageId"]
    ses_event["mail_title"] = ses_event["mail"]["commonHeaders"]["subject"]


def lambda_handler(event, context):
    converted_records = []
    # template_dir = pathlib.Path("/mnt/data")
    # logger.info(list(template_dir.iterdir()))

    for record in event["records"]:
        payload = base64.b64decode(record["data"])
        ses_event = json.loads(payload)
        _add_column(ses_event)
        json_event = json.dumps(ses_event)
        encodedata = base64.b64encode(json_event.encode())
        converted_record = {
            "recordId": record["recordId"],
            "result": "Ok",
            "data": encodedata.decode(),
        }
        converted_records.append(converted_record)

    logger.info(converted_records)
    return {"records": converted_records}
