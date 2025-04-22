resource "aws_s3_bucket" "data" {
    bucket = var.bucket_name
    force_destroy = true
}
