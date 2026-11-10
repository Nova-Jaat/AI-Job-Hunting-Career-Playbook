# Enterprise Generative AI Knowledge Base

## Overview
This platform leverages Amazon Bedrock, OpenSearch Serverless, and AWS EKS to provide low-latency, hallucination-resistant retrieval-augmented generation.

## Key Service Components
1. Amazon Bedrock: Foundation models such as Anthropic Claude 3.5 Sonnet and Amazon Titan Embeddings v2.
2. OpenSearch Serverless: Fully managed vector search using HNSW indexing and cosine similarity.
3. Amazon EKS: Elastic Kubernetes Service hosting FastAPI backend and Next.js frontend with HPA.
4. AWS Lambda: Event-driven document processing triggered automatically on S3 upload.

## SLA & Operational Targets
- P95 Response Latency: < 1.2s for RAG queries.
- Availability: 99.95% multi-AZ deployment across 3 Availability Zones.
