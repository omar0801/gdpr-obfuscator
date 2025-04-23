resource "aws_s3_bucket" "data" {
    bucket = "gdpr-obfuscator-raw"
    force_destroy = true
}

resource "aws_s3_bucket" "obfuscated_data" {
    bucket = "gdpr-obfuscator-obfuscated"
    force_destroy = true
}
