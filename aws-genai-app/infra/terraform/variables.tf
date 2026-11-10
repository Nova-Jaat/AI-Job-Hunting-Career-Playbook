variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "cluster_name" {
  description = "Name of the EKS Cluster"
  type        = string
  default     = "genai-eks-cluster"
}

variable "bedrock_model_id" {
  description = "Primary Bedrock foundation model"
  type        = string
  default     = "anthropic.claude-3-5-sonnet-20241022-v2:0"
}
