resource "aws_s3_bucket" "raw_data" {
    bucket = var.raw_bucket_name
    force_destroy = true
}
