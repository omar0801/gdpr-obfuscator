data "archive_file" "obfuscator" {
  type        = "zip"
  output_file_mode = "0666"
  source_file = "${path.module}/../src/obfuscator.py"
  output_path = "${path.module}/../src/lambda.zip"
}

resource "aws_lambda_function" "obfuscator" {
  function_name = "gdpr-obfuscator"
  role          = aws_iam_role.lambda_role.arn
  handler       = "obfuscator.lambda_handler"
  runtime       = "python3.12"

  filename         = data.archive_file.obfuscator.output_path
  source_code_hash = data.archive_file.obfuscator.output_base64sha256

  timeout = 30
}

resource "aws_lambda_permission" "allow_s3_invoke" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.obfuscator.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.data.arn
}

resource "aws_s3_bucket_notification" "trigger_lambda" {
  bucket = aws_s3_bucket.data.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.obfuscator.arn
    events              = ["s3:ObjectCreated:*"]
  }

  depends_on = [aws_lambda_permission.allow_s3_invoke]
}
