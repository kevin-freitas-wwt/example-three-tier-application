# Infrastructure

The application is deployed to **Google Cloud Platform** using **Terraform** Infrastructure as Code. This provisions a complete, production-ready three-tier architecture with networking, database, and container orchestration.

## Technology Stack

- **Terraform** — Infrastructure as Code
- **Google Cloud Run** — Serverless container platform
- **Cloud SQL** — Managed PostgreSQL database
- **VPC & Networking** — Private networking and security
- **Secret Manager** — Secure credential storage
- **Service Accounts** — Identity and access management

## Project Structure

```
src/infrastructure/
├── main.tf              # Core resource definitions
├── variables.tf         # Input variables
├── outputs.tf           # Output values
├── migration.tf         # Database migration tasks
├── terraform.tfvars.example
└── .gitignore
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│  Google Cloud Platform (VPC)                            │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Cloud Run                                        │  │
│  │  ┌────────────────┐   ┌──────────────────────┐   │  │
│  │  │  Web Service   │──→│  API Service         │   │  │
│  │  │  (Next.js)     │   │  (Express)           │   │  │
│  │  │  Port 3000     │   │  Port 3001           │   │  │
│  │  │  (Public)      │   │  (Internal)          │   │  │
│  │  └────────────────┘   └──────────────────────┘   │  │
│  │         ↓                       ↓                  │  │
│  │    VPC Access Connector                           │  │
│  │  ┌───────────────────────────────────────────┐   │  │
│  └──┤              VPC Network                  ├───┘  │
│     │              (Private)                    │       │
│     │  ┌─────────────────────────────────┐      │       │
│     │  │  Cloud SQL                      │      │       │
│     │  │  PostgreSQL 17                  │      │       │
│     │  │  (Private IP)                   │      │       │
│     │  └─────────────────────────────────┘      │       │
│     │                                           │       │
│     │  ┌─────────────────────────────────┐      │       │
│     │  │  Secret Manager (DB_URL)        │      │       │
│     │  └─────────────────────────────────┘      │       │
│     └───────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────┘
         ↑
         │ HTTPS (Public)
         │
    [ Internet ]
```

## Key Resources

### Networking

**VPC Network** — Isolated network namespace
- Custom VPC (not default)
- Private networking for all resources
- Public internet access only for web frontend

**Subnet** — IP address allocation
- CIDR range (default: 10.0.0.0/24)
- Private Google access enabled
- Region-specific

**VPC Access Connector** — Cloud Run to private services
- Allows Cloud Run to reach Cloud SQL (private IP)
- Machine type: e2-micro
- Min/Max instances: 2/10
- CIDR range (default: 10.0.1.0/28)

**Cloud NAT** — Outbound internet access
- Allows private resources to reach external services
- Configured for the VPC

### Database (Cloud SQL)

**PostgreSQL 17 Instance**
- Tier (configurable): `db-f1-micro` (dev) or larger
- Availability:
  - **Dev/Staging:** Zonal (single zone)
  - **Prod:** Regional (multi-zone high availability)
- Disk type: SSD with auto-resize
- Backups: Enabled in prod, retention configurable
- Deletion protection: Enabled in prod

**Database & User**
- Database name: `app`
- User: `app`
- Password: Auto-generated 32-character random string
- Stored in: Google Secret Manager

**Private IP**
- No public IP exposure
- Only accessible from VPC via VPC Access Connector

### Secret Manager

**Database URL Secret**
- Secret ID: `{app_name}-{environment}-db-url`
- Value: `postgres://app:PASSWORD@PRIVATE_IP:5432/app`
- Replicated across regions for high availability
- Accessed by Cloud Run service account

### Service Accounts

**Cloud Run Service Account**
- Name: `{app_name}-{environment}-run`
- Permissions:
  - Cloud SQL Client (`roles/cloudsql.client`)
  - Secret Manager Secret Accessor (`roles/secretmanager.secretAccessor`)
  - Cloud Run Invoker (for API internal traffic)

### Cloud Run Services

**Web Frontend Service**
- Image: User-provided URI (e.g., `gcr.io/PROJECT/web:latest`)
- Port: 3000
- Ingress: Public (all traffic)
- Scaling:
  - Dev: Min 0, Max 10 instances
  - Prod: Min 1, Max 10 instances
- Memory: 512 MB per instance
- CPU: 1 vCPU per instance
- Probes: Startup (10s delay) and none after
- Environment variables:
  - `PORT=3000`
  - `API_URL={api_service_uri}`

**API Service**
- Image: User-provided URI (e.g., `gcr.io/PROJECT/api:latest`)
- Port: 3001
- Ingress: Internal only (load balancer)
- Scaling:
  - Dev: Min 0, Max 10 instances
  - Prod: Min 1, Max 10 instances
- Memory: 512 MB per instance
- CPU: 1 vCPU per instance
- Probes: Startup (5s delay) and liveness (30s interval)
- Environment variables:
  - `PORT=3001`
  - `DATABASE_URL` (from Secret Manager)

## Input Variables

### Required

```hcl
variable "project_id" {
  description = "GCP project ID"
}

variable "api_image" {
  description = "Container image URI for the API (e.g. gcr.io/PROJECT/api:TAG)"
}

variable "web_image" {
  description = "Container image URI for the web frontend"
}
```

### Optional with Defaults

```hcl
variable "region" {
  default = "us-central1"
  description = "GCP region"
}

variable "app_name" {
  default = "todo"
  description = "Application name prefix"
}

variable "environment" {
  default = "dev"
  description = "Deployment environment (dev, staging, prod)"
  # Validation enforces: dev | staging | prod
}

variable "subnet_cidr" {
  default = "10.0.0.0/24"
}

variable "connector_cidr" {
  default = "10.0.1.0/28"
  # Must be /28 and not overlap with subnet_cidr
}

variable "db_tier" {
  default = "db-f1-micro"
  # Examples: db-f1-micro, db-n1-standard-1, db-n1-standard-4
}

variable "api_max_instances" {
  default = 10
  description = "Cloud Run max instances for API"
}

variable "web_max_instances" {
  default = 10
  description = "Cloud Run max instances for web"
}
```

## Output Values

```hcl
output "web_url"
  # Public URL of the web frontend (e.g., https://todo-dev-web-abc123.run.app)

output "api_url"
  # Internal URL of the API service

output "db_private_ip"
  # Private IP address of Cloud SQL instance

output "db_instance_name"
  # Cloud SQL connection name (PROJECT:REGION:INSTANCE)

output "vpc_name"
  # VPC network name

output "service_account_email"
  # Service account email for Cloud Run

output "db_url_secret_id"
  # Secret Manager secret ID holding DATABASE_URL (sensitive output)
```

## Deployment Process

### Prerequisites

1. **GCP Project** with billing enabled
2. **Service Account** with Editor role (for Terraform)
3. **Terraform** installed locally (>= 1.5)
4. **Docker images** built and pushed to Google Artifact Registry or Container Registry

### Initialize Terraform

```bash
cd src/infrastructure

# Configure GCP authentication
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# Initialize Terraform with GCS backend
terraform init \
  -backend-config=bucket=YOUR_TERRAFORM_STATE_BUCKET \
  -backend-config=prefix=todo/dev
```

### Plan Deployment

```bash
terraform plan \
  -var="project_id=my-project" \
  -var="api_image=gcr.io/my-project/api:latest" \
  -var="web_image=gcr.io/my-project/web:latest" \
  -out=tfplan
```

### Apply Deployment

```bash
terraform apply tfplan
```

This creates all resources and outputs the public web URL.

### Get Outputs

```bash
# View all outputs
terraform output

# Get specific output
terraform output web_url
terraform output api_url

# Extract values programmatically
terraform output -json web_url | jq -r .
```

## Environment-Specific Configuration

### Development

```bash
terraform apply \
  -var="project_id=my-project" \
  -var="environment=dev" \
  -var="db_tier=db-f1-micro" \
  -var="api_image=..." \
  -var="web_image=..."
```

- Min instances: 0 (services scale to zero when not in use)
- HA: Disabled (single zone)
- Backups: Disabled

### Production

```bash
terraform apply \
  -var="project_id=my-project" \
  -var="environment=prod" \
  -var="db_tier=db-n1-standard-2" \
  -var="api_image=..." \
  -var="web_image=..."
```

- Min instances: 1 (always available)
- HA: Enabled (multi-zone with failover)
- Backups: Enabled with retention
- Deletion protection: Enabled

## Cost Optimization

### Reduce Costs in Dev Environment

```hcl
# Lower database tier
db_tier = "db-f1-micro"

# Scale to zero when not in use
web_max_instances = 1
api_max_instances = 1

# Zonal instead of regional
environment = "dev"
```

### High Availability in Prod

```hcl
# Larger database with HA
environment = "prod"

# Minimum 1 instance always running
# Automatic failover enabled
# Backups retained 30+ days
```

## Monitoring and Troubleshooting

### View Cloud Run Logs

```bash
gcloud run services describe {service-name} --region {region}
gcloud run services logs read {service-name} --region {region} --limit 50
```

### Access Cloud SQL

```bash
gcloud sql instances describe {instance-name}

# Connect via Cloud SQL Proxy
cloud-sql-proxy {project}:{region}:{instance-name} &
psql -h localhost -U app -d app
```

### Terraform State

```bash
# Pull remote state for inspection
terraform state pull

# List resources in state
terraform state list

# View specific resource
terraform state show google_sql_database_instance.main
```

## Updating Infrastructure

```bash
# Change a variable
terraform apply \
  -var="db_tier=db-n1-standard-1" \
  -var="web_max_instances=20"

# Update container images
terraform apply \
  -var="api_image=gcr.io/my-project/api:v2" \
  -var="web_image=gcr.io/my-project/web:v2"
```

## Destroying Resources

```bash
# Show what will be deleted
terraform plan -destroy

# Destroy all resources
terraform destroy
```

**Warning:** In prod, deletion protection prevents accidental deletion of the database. You must manually disable it first or set `deletion_protection = false`.

## Local Backend Alternative

For testing without a GCS backend:

```bash
# Use local state file (not recommended for team use)
terraform init
terraform apply ...
```

This creates a `terraform.tfstate` file locally (git-ignored by default).
