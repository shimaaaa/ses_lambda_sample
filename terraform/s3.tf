
# ------------------
# S3
# ------------------

resource "aws_s3_bucket" "seslogtest" {
  bucket = "seslogtest"
  acl    = "private"
}
