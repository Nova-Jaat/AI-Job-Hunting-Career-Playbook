module "vpc" {
  source      = "./modules/vpc"
  vpc_cidr    = var.vpc_cidr
  environment = var.environment
}

module "eks" {
  source             = "./modules/eks"
  cluster_name       = var.cluster_name
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
}

module "opensearch" {
  source          = "./modules/opensearch"
  environment     = var.environment
  collection_name = "genai-kb-${var.environment}"
}

module "bedrock" {
  source            = "./modules/bedrock"
  environment       = var.environment
  oidc_provider_arn = module.eks.oidc_provider_arn
  oidc_issuer       = module.eks.oidc_issuer
}

module "s3" {
  source      = "./modules/s3"
  environment = var.environment
}

module "lambda" {
  source              = "./modules/lambda"
  environment         = var.environment
  s3_bucket_arn       = module.s3.raw_bucket_arn
  s3_bucket_name      = module.s3.raw_bucket_name
  opensearch_endpoint = module.opensearch.collection_endpoint
}
