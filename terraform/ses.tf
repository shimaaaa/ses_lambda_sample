resource "aws_ses_domain_identity" "example" {
  domain = "${var.ses_domain}"
}
resource "aws_route53_record" "example_amazonses_verification_record" {
  zone_id = "Z08639783R6J4ZM5RF3HN"
  name    = "_amazonses.${var.ses_domain}"
  type    = "TXT"
  ttl     = "600"
  records = ["${aws_ses_domain_identity.example.verification_token}"]
}

resource "aws_ses_domain_identity_verification" "example_verification" {
  domain = aws_ses_domain_identity.example.id
  depends_on = [aws_route53_record.example_amazonses_verification_record]
}

resource "aws_ses_domain_dkim" "example" {
  domain = aws_ses_domain_identity.example.domain
}

resource "aws_route53_record" "example_amazonses_dkim_record" {
  count   = 3
  zone_id = "Z08639783R6J4ZM5RF3HN"
  name    = "${element(aws_ses_domain_dkim.example.dkim_tokens, count.index)}._domainkey.${var.ses_domain}"
  type    = "CNAME"
  ttl     = "600"
  records = ["${element(aws_ses_domain_dkim.example.dkim_tokens, count.index)}.dkim.amazonses.com"]
}

resource "aws_ses_configuration_set" "example" {
  name = "ses_log"
}

resource "aws_ses_event_destination" "sns" {
  name                   = "event-destination-sns"
  configuration_set_name = "${aws_ses_configuration_set.example.name}"
  enabled                = true
  matching_types         = ["bounce", "send", "reject", "delivery", "complaint", "open"]

  sns_destination {
    topic_arn = "${aws_sns_topic.example.arn}"
  }
}

resource "aws_sns_topic" "example" {
  name = "ses_log"
}
