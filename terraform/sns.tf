resource "aws_sns_topic" "obfuscation_alerts" {
  name = "gdpr-obfuscator-alerts"
}

resource "aws_sns_topic_subscription" "email_alert" {
  topic_arn = aws_sns_topic.obfuscation_alerts.arn
  protocol  = "email"
  endpoint  = "omar_barouni@hotmail.com"  
}
