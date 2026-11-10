variable "environment" {
  type = string
}

variable "oidc_provider_arn" {
  type = string
}

variable "oidc_issuer" {
  type = string
}

# IAM Policy for Bedrock Access (Least Privilege)
resource "aws_iam_policy" "bedrock_access" {
  name        = "genai-bedrock-access-policy-${var.environment}"
  description = "Allows invoking Bedrock Foundation Models"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "BedrockModelInvocation"
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = [
          "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-5-sonnet-*",
          "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-haiku-*",
          "arn:aws:bedrock:*::foundation-model/amazon.titan-embed-text-*"
        ]
      }
    ]
  })
}

# IRSA Role for EKS Backend Service Account
resource "aws_iam_role" "backend_irsa" {
  name = "genai-backend-irsa-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = var.oidc_provider_arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "${var.oidc_issuer}:sub" = "system:serviceaccount:genai:genai-backend-sa"
          }
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_bedrock" {
  role       = aws_iam_role.backend_irsa.name
  policy_arn = aws_iam_policy.bedrock_access.arn
}

output "backend_role_arn" {
  value = aws_iam_role.backend_irsa.arn
}
