variable "environment" {
  type = string
}

resource "aws_s3_bucket" "docs_raw" {
  bucket = "genai-knowledge-docs-${var.environment}"

  tags = {
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "docs_versioning" {
  bucket = aws_s3_bucket.docs_raw.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "docs_enc" {
  bucket = aws_s3_bucket.docs_raw.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "docs_block" {
  bucket = aws_s3_bucket.docs_raw.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

output "raw_bucket_name" {
  value = aws_s3_bucket.docs_raw.id
}

output "raw_bucket_arn" {
  value = aws_s3_bucket.docs_raw.arn
}
