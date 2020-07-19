import json
import boto3
from datetime import datetime
import pymysql
import os
import logging
import sys

logger = logging.getLogger()
logger.setLevel(logging.INFO)

rds_host = os.environ["RDS_HOST"]
rds_name = os.environ["RDS_USER"]
rds_password = os.environ["RDS_PASSWORD"]
db_name = "ses_log"


s3 = boto3.resource('s3')
s3_bucket = "seslogtest"

def _create_or_update(mail_id, event_type):
    try:
        conn = pymysql.connect(rds_host, user=rds_name, passwd=rds_password, db=db_name, connect_timeout=5)
    except Exception as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")
        logger.exception(e)
        sys.exit()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT count(1) FROM sendmaillog WHERE mail_id = %s"
            cursor.execute(sql, (mail_id,))
            result = cursor.fetchall()
            count = result[0][0]
            if count:
                sql = "UPDATE sendmaillog SET status = %s WHERE mail_id = %s"
                cursor.execute(sql, (event_type, mail_id))
            else:
                sql = "INSERT INTO sendmaillog (mail_id, status) VALUES (%s, %s)"
                cursor.execute(sql, (mail_id, event_type))
    finally:
        conn.close()

def lambda_handler(event, context):
    message = json.loads(event["Records"][0]["Sns"]["Message"])
    request_id = context.aws_request_id
    message_id = message["mail"]["messageId"]
    event_type = message["eventType"]
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{now}__{event_type}__{request_id}.json"
    key = f"{message_id}/{filename}"
    file_contents = json.dumps(message)
    
    _create_or_update(message_id, event_type)
    obj = s3.Object(s3_bucket, key)
    obj.put( Body=file_contents )
    return
