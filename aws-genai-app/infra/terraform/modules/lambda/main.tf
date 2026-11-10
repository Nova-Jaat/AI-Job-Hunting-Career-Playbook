variable "environment" {
  type = string
}

variable "s3_bucket_arn" {
  type = string
}

variable "s3_bucket_name" {
  type = string
}

variable "opensearch_endpoint" {
  type = string
}

resource "aws_iam_role" "lambda_exec" {
  name = "genai-ingestion-lambda-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_policy" "lambda_genai_perms" {
  name = "genai-lambda-perms-${var.environment}"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject"]
        Resource = ["${var.s3_bucket_arn}/*"]
      },
      {
        Effect   = "Allow"
        Action   = ["bedrock:InvokeModel"]
        Resource = ["*"]
      },
      {
        Effect   = "Allow"
        Action   = ["aoss:APIAccessAll"]
        Resource = ["*"]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_attach_custom" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.lambda_genai_perms.arn
}

resource "aws_lambda_function" "ingestion" {
  function_name = "genai-doc-ingestion-${var.environment}"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "ingestion_handler.lambda_handler"
  runtime       = "python3.11"
  timeout       = 300
  memory_size   = 1024

  filename         = "${path.module}/dummy_payload.zip"
  source_code_hash = "dummyhash"

  environment {
    variables = {
      OPENSEARCH_ENDPOINT = var.opensearch_endpoint
      AWS_REGION          = "us-east-1"
    }
  }

  lifecycle {
    ignore_changes = [filename, source_code_hash]
  }
}

resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowExecutionFromS3"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ingestion.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = var.s3_bucket_arn
}

output "lambda_arn" {
  value = aws_lambda_function.ingestion.arn
}
