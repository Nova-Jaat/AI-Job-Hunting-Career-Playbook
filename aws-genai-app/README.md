# ☁️🤖 AWS + GenAI – Complete Production Architecture 🚀

Build, deploy, scale, and monitor production-ready Generative AI applications on AWS using **Amazon Bedrock**, **EKS**, **Lambda**, **S3**, **RAG**, **OpenSearch Serverless**, and **CloudWatch**.

---

## 🏗️ Architecture Overview

```mermaid
flowchart TD
    User([User / Web / Mobile]) --> Route53[Amazon Route 53]
    Route53 --> CloudFront[CloudFront CDN]
    CloudFront --> ALB[Application Load Balancer]
    
    subgraph VPC["AWS VPC (Multi-AZ Private Subnets)"]
        subgraph EKS["Amazon EKS Cluster"]
            Frontend["Frontend (Next.js)"]
            Backend["Backend (FastAPI)"]
            RAG["RAG Pipeline (LangChain/Boto3)"]
            HPA["Horizontal Pod Autoscaler"]
        end
        
        AOSS[("OpenSearch Serverless\n(Vector Index - HNSW)")]
        RDS[("Amazon Aurora RDS\n(App Metadata)")]
    end
    
    ALB --> Frontend
    Frontend --> Backend
    Backend --> RAG
    
    RAG <--> AOSS
    RAG <--> Bedrock["Amazon Bedrock\n(Claude 3.5 Sonnet / Titan v2)"]
    Backend <--> RDS
    
    subgraph Ingestion["Automated Document Ingestion"]
        S3[("Amazon S3 Bucket\n(Raw Docs / PDFs)")] -->|S3 Event| Lambda["AWS Lambda Ingestion"]
        Lambda -->|Chunk & Titan Embed| Bedrock
        Lambda -->|Write Vectors| AOSS
    end
    
    subgraph Observability["Production Observability & Security"]
        CW["CloudWatch (Logs/Metrics/Alarms)"]
        XRay["AWS X-Ray (Tracing)"]
        IAM["IAM Least Privilege (IRSA)"]
        SM["Secrets Manager"]
        SNS["SNS Alerting"]
    end
    
    EKS -.-> CW
    EKS -.-> XRay
    EKS -.-> IAM
```

---

## 📁 Repository Structure

```
aws-genai-app/
├── .github/workflows/ci-cd.yml      # GitHub Actions CI/CD (Trivy, ECR, Helm)
├── infra/terraform/                 # Terraform Infrastructure as Code
│   ├── main.tf                      # Root module orchestrating all resources
│   ├── providers.tf                 # AWS, Kubernetes, Helm providers & remote state
│   ├── variables.tf                 # Global environment variables
│   ├── outputs.tf                   # Endpoints and ARNs
│   └── modules/                     # VPC, EKS, Bedrock, OpenSearch, S3, Lambda
├── helm/genai-app/                  # Kubernetes Helm Charts
│   ├── Chart.yaml                   # Chart metadata
│   ├── values.yaml                  # Production configs, IRSA, resource limits
│   └── templates/                   # Deployments, Services, Ingress, HPA
├── src/
│   ├── backend/                     # FastAPI backend application
│   │   ├── app/
│   │   │   ├── main.py              # Application entrypoint & probes
│   │   │   ├── routes.py            # Chat & ingestion REST endpoints
│   │   │   ├── rag_pipeline.py      # Bedrock + OpenSearch RAG logic
│   │   │   ├── bedrock_client.py    # Claude 3.5 Sonnet & Titan Embeddings
│   │   │   ├── vector_store.py      # OpenSearch Serverless k-NN & Hybrid search
│   │   │   └── utils.py             # Recursive text chunking
│   │   ├── Dockerfile               # Multi-stage hardened container image
│   │   └── requirements.txt         # Python dependencies
│   ├── frontend/                    # Next.js UI
│   │   ├── app/page.tsx             # Interactive RAG chat UI with citations
│   │   ├── Dockerfile               # Production Next.js standalone container
│   │   └── package.json
│   └── lambda/                      # S3 Document Ingestion Lambda
│       ├── ingestion_handler.py     # PDF parsing, chunking, Titan embeddings
│       └── requirements.txt
├── data/documents/                  # Source documents for knowledge base
├── tests/                           # Pytest unit & integration test suite
├── scripts/                         # deploy.sh and ingest_data.sh automation
├── docker-compose.yml               # Local stack testing configuration
└── README.md
```

---

## ⚡ Quick Start

### 1. Local Testing with Docker Compose
```bash
docker-compose up --build
```
- Frontend UI: `http://localhost:3000`
- FastAPI Docs: `http://localhost:8000/docs`

### 2. Infrastructure Deployment (AWS)
```bash
cd infra/terraform
terraform init
terraform apply -var="environment=prod"
```

### 3. Deploy Kubernetes App (Helm)
```bash
aws eks update-kubeconfig --name genai-eks-cluster --region us-east-1
helm upgrade --install genai-app helm/genai-app -n genai --create-namespace
```
