# 🚀 Production Cloud & DevOps Engineering Mastery Blueprint
> **Personalized for Sanjeev Kumar** | RHCSA Certified | Target: Senior Cloud & Platform DevOps Engineer

---

## 📌 Executive Summary & Profile Baseline

This blueprint provides an end-to-end, production-grade roadmap designed to bridge the gap between your current **RHCSA Linux & Cloud Infrastructure** foundation and the **Senior Platform / DevOps Engineer** standard. 

It synthesizes:
1. **Your Current Verified Skills** (RHCSA on RHEL 9, AWS VPC & Networking, Modular Terraform, Docker, Azure Functions).
2. **The 10 Production Projects** required for elite-tier roles.
3. **The Curriculum & Mock Interview Banks** from `CloudDevOpsHub/MultiCloud-DevOps-AI-Challenge`.
4. **Market Standards for 2026**: GitOps, Zero-Trust Cloud IAM (OIDC/IRSA), Shift-Left DevSecOps, and Observability.

---

## 👤 Baseline Assessment & Skill Matrix

```
┌───────────────────────────────┬───────────────────────────────┬──────────────────────────────┐
│ Verified Current Baseline     │ Expansion In Progress         │ Target Mastered State        │
├───────────────────────────────┼───────────────────────────────┼──────────────────────────────┤
│ • RHEL 9 (RHCSA 221/300)      │ • GitHub Actions CI/CD        │ • Enterprise GitOps (ArgoCD) │
│ • LVM, systemd, SSH hardening │ • Trivy Container Scanning    │ • Argo Rollouts (Canary/B-G) │
│ • AWS VPC, Subnets, NAT, IGW  │ • Basic Helm Charts           │ • Multi-Tenant EKS & RBAC    │
│ • S3 + CloudFront (OAC)       │ • EKS Terraform Modules       │ • External Secrets (ESO)     │
│ • Modular Terraform HCL       │ • Azure DevOps Boards/Repos   │ • Kube-Prometheus + Loki     │
│ • Dockerfile & Containers     │ • CloudWatch Alarms           │ • Karpenter Autoscaling      │
└───────────────────────────────┴───────────────────────────────┴──────────────────────────────┘
```

---

## 🗺️ Master Curriculum Mapping (MultiCloud Challenge Integration)

We adapt the **CloudDevOpsHub 55-Session & 8-Project Curriculum** directly to your strengths:

| Phase | Sessions | Module Focus | Sanjeev's Action Plan |
|---|---|---|---|
| **Phase 0** | S00–S09 | Linux Admin + GCP Basics | **Fast-Track**: Verify core commands; take `Mock-01` directly. |
| **Phase 1** | S10–S21, S38–S39 | AWS Core Deep Dive + IaC | **Build Project 3 & 4**: Terraform ALB, ASG, RDS Multi-AZ, ECS Fargate. |
| **Phase 2** | S22–S29, S50, S53 | CI/CD + DevSecOps | **Build Project 1 & 6**: GitHub Actions + Jenkins + Trivy + Gitleaks + SonarQube. |
| **Phase 3** | S30–S37, S51, S56 | Containers, K8s & Observability | **Build Project 2, 5 & 7**: Production EKS, Helm, Prometheus, Grafana, Loki. |
| **Phase 4** | S47–S49, S54 | Azure DevOps & Cloud Secrets | **Build Project 9 & Azure DevOps**: HashiCorp Vault / ESO + Azure Pipelines. |
| **Phase 5** | S55, S57, S59 | Progressive Delivery & Capstone | **Build Project 8 & 10**: ArgoCD Rollouts + End-to-End Platform + MCP Server. |

---

## 🏗️ Deep-Dive: The 10 Production Projects

```
                                 [10. END-TO-END PLATFORM CAPSTONE]
                                                  ▲
                   ┌──────────────────────────────┴──────────────────────────────┐
                   │                                                             │
         [8. ZERO-DOWNTIME GITOPS]                                     [5. OBSERVABILITY STACK]
           ArgoCD + Argo Rollouts                                        Prometheus + Grafana + Loki
                   ▲                                                             ▲
                   │                                                             │
         [7. PRODUCTION AWS EKS]                                       [9. SECRETS MANAGEMENT]
         Multi-AZ, ALB Ingress, RBAC                                     External Secrets Operator
                   ▲                                                             ▲
                   ├──────────────────────────────┬──────────────────────────────┘
                   │                               │
         [1 & 6. DEVSECOPS CI/CD]        [4. ENTERPRISE ECS FARGATE]
         Gitleaks + Sonar + Trivy         Serverless Containers + ALB
                   ▲                               ▲
                   │                               │
                   └───────────────┬───────────────┘
                                   │
                   [3. THREE-TIER INFRASTRUCTURE]
                    Terraform + ALB + ASG + RDS
```

---

### Project 1 & 6: Production DevSecOps CI/CD Pipeline
* **Goal**: Build an automated "Shift-Left" pipeline where security, linting, scanning, and container packaging occur on every Git push.
* **Tech Stack**: GitHub Actions, Docker, Trivy, SonarCloud, Gitleaks, AWS ECR.
* **Architecture**:
  ```
  Developer Push ──▶ Gitleaks (Secrets) ──▶ SonarCloud (SAST) ──▶ Unit Tests 
         ──▶ Docker Multi-Stage Build ──▶ Trivy (CVE Scan) ──▶ AWS ECR (OIDC)
  ```
* **Production Standards**:
  1. Authenticate to AWS via **OIDC (OpenID Connect)**. Never hardcode `AWS_ACCESS_KEY_ID`.
  2. Multi-stage Dockerfile running as a non-root user (`USER 10001`).
  3. `trivy` fails the build on `CRITICAL` or `HIGH` unfixed CVEs (`--exit-code 1`).
  4. Immutable image tags tied to Git Commit SHA (`$GITHUB_SHA`), never `:latest`.

---

### Project 3: Three-Tier Web Application Infrastructure
* **Goal**: Provision highly available, self-healing multi-tier cloud infrastructure in pure Terraform.
* **Tech Stack**: Terraform, AWS VPC, EC2, ALB, Auto Scaling (ASG), Amazon RDS, IAM.
* **Architecture**:
  * **Public Subnets**: Internet Gateway, Application Load Balancer (ALB), NAT Gateways.
  * **Private App Subnets**: Auto Scaling Group of EC2 instances running app servers.
  * **Private DB Subnets**: Amazon RDS (PostgreSQL/MySQL) Multi-AZ instance; strictly no internet route.
* **Production Standards**:
  1. Remote State Backend: AWS S3 with AES-256 encryption + DynamoDB state locking.
  2. Security Groups: ALB allows `80/443` from `0.0.0.0/0`. EC2 allows app port only from the ALB security group. RDS allows `5432/3306` only from the EC2 security group.
  3. Automated user-data script to bootstrap applications and log output to `/var/log/user-data.log`.

---

### Project 4: Enterprise ECS Fargate Platform
* **Goal**: Run scalable, serverless containers without managing underlying EC2 operating systems.
* **Tech Stack**: Terraform, AWS ECS Fargate, ALB, CloudWatch, AWS ECR.
* **Architecture**:
  * Container images pulled securely from private AWS ECR.
  * ECS Fargate Tasks deployed across multiple Availability Zones in private subnets.
  * ALB Target Group dynamically tracking Fargate Task IP addresses.
* **Production Standards**:
  1. Separation of IAM roles: `task_execution_role` (ECR pull, CloudWatch logs) vs `task_role` (runtime application permissions).
  2. Service Auto Scaling: Target tracking scaling policy based on `ECSServiceAverageCPUUtilization` (target: 65%).
  3. Container health checks configured in both Task Definition and ALB Target Group.

---

### Project 2 & 7: Production AWS EKS Kubernetes Platform
* **Goal**: Architect an enterprise-ready Kubernetes cluster with multi-tenancy, custom networking, and dynamic autoscaling.
* **Tech Stack**: Terraform, AWS EKS, Helm, AWS Load Balancer Controller, Karpenter / HPA, RBAC.
* **Key Components**:
  1. **EKS Cluster**: Managed Node Groups across 3 AZs with mixed On-Demand and Spot instances.
  2. **AWS Load Balancer Controller**: Installed via Helm with IRSA to dynamically provision ALBs from Kubernetes `Ingress` manifests.
  3. **Multi-Tenancy & Governance**:
     * Namespaces: `development`, `staging`, `production`.
     * `ResourceQuotas` and `LimitRanges` preventing runaway memory/CPU consumption.
     * `NetworkPolicies` isolating inter-namespace pod communication.
  4. **Autoscaling**:
     * **HPA (Horizontal Pod Autoscaler)**: Scales pod replicas based on CPU/memory utilization.
     * **Karpenter**: Sub-minute just-in-time node provisioning directly calling AWS EC2 fleet APIs.

---

### Project 5: Complete Observability & Alerting Stack
* **Goal**: Full-stack telemetry covering cluster metrics, distributed application logs, and actionable alerts.
* **Tech Stack**: Prometheus Operator (kube-prometheus-stack), Grafana, Grafana Loki, Promtail, Alertmanager.
* **Telemetry Layers**:
  * **Metrics**: `node-exporter` (host metrics), `kube-state-metrics` (k8s object state), application `/metrics`.
  * **Logs**: Promtail DaemonSet collecting container logs from `/var/log/pods` and shipping to Loki.
  * **Dashboards**: Grafana dashboards tracking Kubernetes cluster health, Pod CPU throttling, and Ingress 4xx/5xx rates.
  * **Alerting**: Alertmanager rules triggering alerts for `CrashLoopBackOff`, Pod `OOMKilled`, Disk `SpaceFillingUp`, and High Latency.

---

### Project 9: Centralized Secrets Management
* **Goal**: Enforce zero secrets in Git or plaintext manifests using runtime synchronization.
* **Tech Stack**: AWS Secrets Manager / HashiCorp Vault, Kubernetes, External Secrets Operator (ESO), IRSA.
* **Workflow**:
  ```
  Developer commits ExternalSecret CRD (references secret name) 
         ──▶ External Secrets Operator authenticates to AWS via IRSA 
         ──▶ Fetches encrypted secret from AWS Secrets Manager 
         ──▶ Generates native in-memory Kubernetes Secret object
  ```
* **Production Standards**:
  1. Pods mount secrets as environment variables or memory-backed (`tmpfs`) volume mounts.
  2. Automatic secret rotation: When the secret updates in AWS, ESO synchronizes and triggers a rolling pod restart via Reloader.

---

### Project 8: Zero-Downtime Deployment Platform (GitOps)
* **Goal**: Modern progressive delivery platform using declarative GitOps and Canary deployment verification.
* **Tech Stack**: ArgoCD, Argo Rollouts, Helm, Kubernetes, Prometheus.
* **Workflow**:
  1. **GitOps Engine (ArgoCD)**: Monitors the `k8s-manifests` Git repository and continuously reconciles desired state with live cluster state.
  2. **Canary Releases (Argo Rollouts)**:
     * Step 1: Route 10% traffic to Canary pods.
     * Step 2: Run automated `AnalysisTemplate` querying Prometheus for 5 minutes (`http_requests_total{status=~"5.*"}`).
     * Step 3: If error rate < 0.5%, promote to 50%, then 100%. If error rate spikes, immediately abort and rollback traffic.

---

### Project 10: The Capstone End-to-End DevOps Platform
* **Goal**: The unified portfolio showcase integrating all 9 projects into an automated developer experience.
* **Deliverable**:
  * Infrastructure provisioned by Terraform in a single clean run.
  * Microservice repositories running GitHub Actions DevSecOps workflows.
  * ArgoCD orchestrating Helm deployments onto AWS EKS.
  * ESO handling runtime credentials and Prometheus/Grafana monitoring traffic.

---

## 🛠️ The "Unspoken" Production Skills

Top-tier engineers are evaluated on how they handle **failures, diagnostics, and edge cases**:

### 1. Production Linux & Network Diagnostics
* **DNS Resolution inside Kubernetes**: Diagnosing `/etc/resolv.conf`, the impact of `ndots:5`, and CoreDNS latency.
* **Memory & Process Failures**: Distinguishing between `OOMKilled` (Exit code 137, Linux kernel killer) and CPU Throttling (`cpu.cfs_quota_us`).
* **The Ephemeral Debug Pod**:
  ```bash
  kubectl debug -it <pod-name> --image=nicolaka/netshoot -- /bin/bash
  # Inside netshoot:
  nc -zv <db-hostname> 5432       # Test TCP connection
  dig +trace api.internal         # Trace DNS hierarchy
  tcpdump -nn -i any port 80      # Inspect packet traffic
  ```

### 2. Resilient Infrastructure as Code
* **Refactoring without Destruction**: Using Terraform `moved` blocks to rename or modularize resources without destroying production databases.
* **State Drift Resolution**: Handling state locks (`terraform force-unlock`) and reconciling out-of-band AWS console changes.
* **PR Cost & Security Guardrails**: Integrating `infracost` and `checkov` directly into Pull Requests.

---

## 🏢 Work Culture: A Day in the Life of a Cloud/DevOps Engineer

DevOps is an **Internal Platform Engineering** team that enables product developers to deliver software safely and quickly.

### ⏰ Daily Workflow

* **09:30 AM – Morning Pulse & Alert Review**:
  * Open Slack `#alerts-prod` and review Grafana cluster dashboards.
  * Check overnight pod crash rates, error budgets, and cloud spending trends.
* **10:00 AM – Standup (15 Mins)**:
  * Concise updates: What you completed, what you're deploying today, and blockers.
* **10:15 AM - 01:00 PM – Deep Engineering Work**:
  * Writing modular Terraform or Helm charts.
  * Testing locally first using `kind` (Kubernetes in Docker) to prevent cloud billing.
  * Opening Git Pull Requests with automated linter and security checks.
* **01:00 PM - 02:00 PM – Lunch & Tech Architecture Discussion**:
  * Reviewing RFCs (Request for Comments), e.g., migrating from Cluster Autoscaler to Karpenter.
* **02:00 PM - 03:30 PM – Developer Enablement & Peer Reviews**:
  * Reviewing developer Dockerfiles to ensure multi-stage builds, non-root users, and proper health checks.
  * Assisting a backend developer debugging connection timeouts in staging.
* **03:30 PM - 05:00 PM – Eliminating "Toil"**:
  * Automating manual tasks. If done manually twice, script or automate it via CronJobs/Lambdas.
* **05:00 PM - 06:00 PM – Deployments & Async Wrap-Up**:
  * Reconcile changes in staging via ArgoCD, check off sprint tickets, and ensure on-call alerts are active.

---

## 🎙️ Mock Interview Question Banks & Mastery Drills

Mapped to the **CloudDevOpsHub Mock Interview Modules**:

### Mock Round 1: Linux, Networking & Foundations (`Mock-01`)
1. *How does the Linux kernel handle memory allocation, and what triggers an OOM killer?*
2. *Walk me through the lifecycle of a packet when a client executes `curl https://api.mycompany.com`.*
3. *How do you inspect live open sockets and listening ports without netstat?* (`ss -tulpn`)
4. *Explain the difference between LVM thin provisioning and standard logical volumes.*

### Mock Round 2: AWS Core Services & Networking (`Mock-02`)
1. *What is the difference between a Security Group and a Network ACL at the packet level?*
2. *How does an Application Load Balancer determine if a target instance is healthy?*
3. *Why should database instances be placed in private subnets with no NAT Gateway attached?*
4. *Explain how IAM Role assumption works using AWS STS temporary credentials.*

### Mock Round 3: CI/CD & DevSecOps (`Mock-03`)
1. *How do you securely connect GitHub Actions to AWS without static access keys? (Explain OIDC).*
2. *What is the difference between SAST, DAST, and Container Vulnerability Scanning?*
3. *How do you configure a quality gate in SonarQube to block builds failing coverage or vulnerability rules?*
4. *How do you ensure Docker build caching works efficiently in remote CI runners?*

### Mock Round 4: Docker & Production Kubernetes (`Mock-04`)
1. *What happens inside the Linux kernel when a container starts? (Namespaces and Cgroups).*
2. *Explain the difference between a ClusterIP, NodePort, and LoadBalancer service.*
3. *What are the three Kubernetes probes (startup, liveness, readiness), and what happens when readiness fails?*
4. *How does CoreDNS resolve service names within the cluster?*

### Mock Round 5: Terraform & Infrastructure as Code (`Mock-05`)
1. *How does Terraform manage state locking when multiple engineers run plans simultaneously?*
2. *What is the difference between Terraform `taint`, `refresh-only`, and `moved` blocks?*
3. *How do you manage sensitive values in Terraform outputs and state files?*
4. *Explain how you structure reusable Terraform modules for Dev, Staging, and Production.*

### Mock Round 6: GitOps, Secrets & Observability (`Mock-06` to `Mock-08`)
1. *Explain the architectural difference between Push-based CI/CD and Pull-based GitOps (ArgoCD).*
2. *How does External Secrets Operator (ESO) retrieve secrets from AWS Secrets Manager using IRSA?*
3. *Explain the difference between Prometheus Counter, Gauge, Histogram, and Summary metrics.*
4. *Describe a real production troubleshooting scenario where you used Grafana and Loki to diagnose a 504 Gateway Timeout.*

---

## 📚 Curated Learning & Reference Vault

### 📺 High-Quality YouTube Engineering Channels
* **[Anton Putra](https://www.youtube.com/@AntonPutra)**: Gold standard for production Terraform, EKS, Karpenter, and Prometheus.
* **[Abhishek Veeramalla](https://www.youtube.com/@AbhishekVeeramalla)**: Excellent DevSecOps pipelines, Jenkins, and interview preparation.
* **[Hussein Nasser](https://www.youtube.com/@hnasr)**: Master-class networking, TCP/IP, reverse proxies, and TLS.
* **[The DevOps Toolkit (Viktor Farcic)](https://www.youtube.com/@DevOpsToolkit)**: Progressive delivery, ArgoCD, and architectural comparisons.

### 💻 GitHub Repositories for Daily Hands-On Practice
* **[`CloudDevOpsHub/MultiCloud-DevOps-AI-Challenge`](https://github.com/CloudDevOpsHub/MultiCloud-DevOps-AI-Challenge)**: Primary curriculum and practical sessions.
* **[`bregman-arie/devops-exercises`](https://github.com/bregman-arie/devops-exercises)**: 2,600+ exercises on Linux, AWS, Docker, K8s, and Terraform.
* **[`antonputra/tutorials`](https://github.com/antonputra/tutorials)**: Production HCL and YAML code for real clusters.
* **[`kelseyhightower/kubernetes-the-hard-way`](https://github.com/kelseyhightower/kubernetes-the-hard-way)**: The definitive guide to Kubernetes internals.

### 🌐 Free Sandboxes (Zero Cloud Cost)
* **[Killercoda](https://killercoda.com)**: Free, instant in-browser Linux & Kubernetes clusters for practicing manifests and Helm.
* **[AWS EKS Workshop](https://eksworkshop.com)**: Official AWS step-by-step production guides.

---

## 🏁 Immediate Action Checklist

- [ ] **Step 1**: Review the 10 project architectures above.
- [ ] **Step 2**: Initialize **Project 3 (Three-Tier Terraform Infrastructure)** in this workspace.
- [ ] **Step 3**: Scaffold modular Terraform layout (`modules/vpc`, `modules/alb`, `modules/asg`, `modules/rds`).
- [ ] **Step 4**: Complete the first mock drill from `Mock-01` & `Mock-02`.
