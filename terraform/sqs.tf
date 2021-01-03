# ------------------
# SQS
# ------------------
resource "aws_sqs_queue" "ses_send_mail_dlq" {
  name = "ses_send_mail_dlq"
  delay_seconds = 30
  max_message_size = 2048
  message_retention_seconds = 86400
  receive_wait_time_seconds = 10
}

resource "aws_sqs_queue" "ses_send_mail" {
  name = "ses_send_mail"
  delay_seconds = 30
  max_message_size = 2048
  visibility_timeout_seconds = 600
  message_retention_seconds = 86400
  receive_wait_time_seconds = 10
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.ses_send_mail_dlq.arn
    maxReceiveCount     = 2
  })
}
