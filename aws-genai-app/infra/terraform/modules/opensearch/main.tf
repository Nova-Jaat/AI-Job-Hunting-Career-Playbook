variable "environment" {
  type = string
}

variable "collection_name" {
  type    = string
  default = "genai-knowledge-base"
}

# Encryption Security Policy
resource "aws_opensearchserverless_security_policy" "encryption" {
  name = "${var.collection_name}-enc"
  type = "encryption"
  policy = jsonencode({
    Rules = [
      {
        ResourceType = "collection"
        Resource     = ["collection/${var.collection_name}"]
      }
    ]
    AWSOwnedKey = true
  })
}

# Network Security Policy
resource "aws_opensearchserverless_security_policy" "network" {
  name = "${var.collection_name}-net"
  type = "network"
  policy = jsonencode([
    {
      Rules = [
        {
          ResourceType = "collection"
          Resource     = ["collection/${var.collection_name}"]
        },
        {
          ResourceType = "dashboard"
          Resource     = ["collection/${var.collection_name}"]
        }
      ]
      AllowFromPublic = true
    }
  ])
}

# OpenSearch Serverless Vector Collection
resource "aws_opensearchserverless_collection" "vector_db" {
  name       = var.collection_name
  type       = "VECTORSEARCH"
  depends_on = [aws_opensearchserverless_security_policy.encryption]

  tags = {
    Environment = var.environment
  }
}

output "collection_endpoint" {
  value = aws_opensearchserverless_collection.vector_db.collection_endpoint
}

output "collection_arn" {
  value = aws_opensearchserverless_collection.vector_db.arn
}
