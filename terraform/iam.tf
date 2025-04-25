resource "aws_iam_role" "lambda_role" {
    name = "project_lambda_role"
    assume_role_policy = <<EOF
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "sts:AssumeRole"
                ],
                "Principal": {
                    "Service": [
                        "lambda.amazonaws.com"
                    ]
                }
            }
        ]
    }
    EOF
}


resource "aws_iam_policy_attachment" "lambda_logging" {
  name       = "lambda-logging"
  roles      = [aws_iam_role.lambda_role.name]
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_policy" "s3_access" {
  name = "lambda-s3-access"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ],
        Resource = [
          "arn:aws:s3:::gdpr-obfuscator-raw/*",
          "arn:aws:s3:::gdpr-obfuscator-obfuscated/*"
        ]
      }
    ]
  })
}

resource "aws_iam_policy_attachment" "attach_s3_access" {
  name       = "attach-lambda-s3"
  roles      = [aws_iam_role.lambda_role.name]
  policy_arn = aws_iam_policy.s3_access.arn
}

resource "aws_iam_policy" "sns_publish" {
  name = "lambda-sns-publish"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = "sns:Publish",
        Resource = aws_sns_topic.obfuscation_alerts.arn
      }
    ]
  })
}

resource "aws_iam_policy_attachment" "attach_sns_publish" {
  name       = "lambda-sns-publish"
  roles      = [aws_iam_role.lambda_role.name]
  policy_arn = aws_iam_policy.sns_publish.arn
}
