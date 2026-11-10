#!/usr/bin/env bash
set -euo pipefail

ENV=${1:-prod}
REGION=${2:-us-east-1}

echo "🚀 Deploying AWS GenAI Architecture for environment: $ENV in $REGION"

# 1. Apply Terraform Infrastructure
echo "==> Step 1: Initializing & Applying Terraform..."
cd infra/terraform
terraform init
terraform apply -var="environment=$ENV" -var="aws_region=$REGION" -auto-approve

# 2. Extract Outputs
CLUSTER_NAME=$(terraform output -raw eks_cluster_name)
ECR_BACKEND_ROLE=$(terraform output -raw backend_irsa_role_arn)
cd ../..

# 3. Update Kubeconfig
echo "==> Step 2: Configuring kubectl context..."
aws eks update-kubeconfig --name "$CLUSTER_NAME" --region "$REGION"

# 4. Deploy Helm Chart
echo "==> Step 3: Deploying GenAI Application Helm Chart..."
helm upgrade --install genai-app ./helm/genai-app \
  --namespace genai \
  --create-namespace \
  --values ./helm/genai-app/values.yaml

echo "✅ Production GenAI App Deployed Successfully!"
