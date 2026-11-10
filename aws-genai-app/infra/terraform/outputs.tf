output "eks_cluster_name" {
  value = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  value = module.eks.cluster_endpoint
}

output "opensearch_endpoint" {
  value = module.opensearch.collection_endpoint
}

output "backend_irsa_role_arn" {
  value = module.bedrock.backend_role_arn
}

output "s3_ingestion_bucket" {
  value = module.s3.raw_bucket_name
}
