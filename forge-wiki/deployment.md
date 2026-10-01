# Deployment

This guide walks through deploying the three-tier application to **Google Cloud Platform** using **Terraform**.

## Quick Start

### 1. Prepare Docker Images

Build and push container images to Google Artifact Registry:

```bash
# Set up Artifact Registry
gcloud artifacts repositories create todo-repo \
  --repository-format=docker \
  --location=us-central1

# Build and push API image
docker build -t us-central1-docker.pkg.dev/MY_PROJECT/todo-repo/api:latest ./src/api
docker push us-central1-docker.pkg.dev/MY_PROJECT/todo-repo/api:latest

# Build and push web image
docker build -t us-central1-docker.pkg.dev/MY_PROJECT/todo-repo/web:latest ./src/web
docker push us-central1-docker.pkg.dev/MY_PROJECT/todo-repo/web:latest
```

### 2. Set Up Terraform Backend

Create a GCS bucket for Terraform state:

```bash
# Create bucket
gsutil mb gs://MY_PROJECT-terraform-state

# Enable versioning
gsutil versioning set on gs://MY_PROJECT-terraform-state
```

### 3. Initialize and Deploy

```bash
cd src/infrastructure

# Initialize Terraform
terraform init \
  -backend-config=bucket=MY_PROJECT-terraform-state \
  -backend-config=prefix=todo/dev

# Plan the deployment
terraform plan \
  -var="project_id=MY_PROJECT" \
  -var="api_image=us-central1-docker.pkg.dev/MY_PROJECT/todo-repo/api:latest" \
  -var="web_image=us-central1-docker.pkg.dev/MY_PROJECT/todo-repo/web:latest" \
  -var="environment=dev" \
  -out=tfplan

# Apply the plan
terraform apply tfplan

# Get the public URL
terraform output web_url
```

## Detailed Deployment Guide

### Prerequisites

Before deploying, ensure you have:

1. **GCP Project** with billing enabled
2. **gcloud CLI** installed and authenticated
3. **Terraform** installed (>= 1.5)
4. **Docker** installed (for building images)
5. Access to the GCP project with:
   - Compute Admin role
   - Cloud SQL Admin role
   - Service Account Admin role
   - Secret Manager Admin role

### Step 1: Configure GCP Authentication

#### Option A: Service Account (Recommended for CI/CD)

```bash
# Create service account
gcloud iam service-accounts create terraform-sa \
  --display-name="Terraform Service Account"

# Grant permissions
gcloud projects add-iam-policy-binding MY_PROJECT \
  --member=serviceAccount:terraform-sa@MY_PROJECT.iam.gserviceaccount.com \
  --role=roles/editor

# Create and download key
gcloud iam service-accounts keys create terraform-key.json \
  --iam-account=terraform-sa@MY_PROJECT.iam.gserviceaccount.com

# Export for Terraform
export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/terraform-key.json
```

#### Option B: User Account (For local testing)

```bash
gcloud auth application-default login
```

### Step 2: Build and Push Container Images

#### Create Artifact Registry Repository

```bash
# Create repository
gcloud artifacts repositories create example-three-tier \
  --repository-format=docker \
  --location=us-central1 \
  --description="Three-tier application images"

# Configure Docker auth
gcloud auth configure-docker us-central1-docker.pkg.dev
```

#### Build and Push Images

```bash
cd /path/to/repository

# Build API image
docker build -t us-central1-docker.pkg.dev/MY_PROJECT/example-three-tier/api:v1.0 ./src/api
docker push us-central1-docker.pkg.dev/MY_PROJECT/example-three-tier/api:v1.0

# Build web image
docker build -t us-central1-docker.pkg.dev/MY_PROJECT/example-three-tier/web:v1.0 ./src/web
docker push us-central1-docker.pkg.dev/MY_PROJECT/example-three-tier/web:v1.0

# Or use 'latest' tag for development
docker build -t us-central1-docker.pkg.dev/MY_PROJECT/example-three-tier/api:latest ./src/api
docker push us-central1-docker.pkg.dev/MY_PROJECT/example-three-tier/api:latest
```

### Step 3: Create Terraform Backend

```bash
# Create GCS bucket for state
gsutil mb gs://MY_PROJECT-terraform

# Enable versioning
gsutil versioning set on gs://MY_PROJECT-terraform

# Create folder structure (optional)
echo "placeholder" | gsutil cp - gs://MY_PROJECT-terraform/todo/dev/placeholder
```

### Step 4: Initialize Terraform

```bash
cd src/infrastructure

# Download Terraform providers
terraform init \
  -backend-config=bucket=MY_PROJECT-terraform \
  -backend-config=prefix=todo/dev
```

After initialization, you should see:
```
Terraform has been successfully configured!
```

### Step 5: Review and Deploy

```bash
# Create terraform.tfvars with your values
cat > terraform.tfvars <<EOF
project_id = "MY_PROJECT"
region = "us-central1"
app_name = "todo"
environment = "dev"
api_image = "us-central1-docker.pkg.dev/MY_PROJECT/example-three-tier/api:v1.0"
web_image = "us-central1-docker.pkg.dev/MY_PROJECT/example-three-tier/web:v1.0"
db_tier = "db-f1-micro"
api_max_instances = 5
web_max_instances = 5
EOF

# Review planned changes
terraform plan

# Apply the plan
terraform apply

# View outputs
terraform output
```

### Step 6: Access Your Deployment

```bash
# Get the public URL
FRONTEND_URL=$(terraform output -raw web_url)
echo "Frontend: $FRONTEND_URL"

# Get API URL
API_URL=$(terraform output -raw api_url)
echo "API: $API_URL"

# Test the health endpoint
curl $API_URL/health
```

## Database Setup and Verification

After deployment, the database is automatically initialized via Cloud Run migrations:

```bash
# Check migration job status
gcloud run jobs list --region=us-central1

# View migration logs
gcloud run jobs log-tail MIGRATION_JOB_NAME --region=us-central1
```

If manual database interaction is needed:

```bash
# Connect to Cloud SQL instance using Cloud SQL Proxy
cloud-sql-proxy MY_PROJECT:us-central1:todo-dev-postgres &

# Connect via psql
psql -h localhost -U app -d app

# View tasks
SELECT * FROM tasks;
```

## Updating a Deployment

### Update Container Images

```bash
# Rebuild images with new tag
docker build -t us-central1-docker.pkg.dev/MY_PROJECT/example-three-tier/api:v1.1 ./src/api
docker push us-central1-docker.pkg.dev/MY_PROJECT/example-three-tier/api:v1.1

# Update Terraform
terraform apply \
  -var="api_image=us-central1-docker.pkg.dev/MY_PROJECT/example-three-tier/api:v1.1"
```

### Scale Resources

```bash
# Increase max instances
terraform apply \
  -var="api_max_instances=20" \
  -var="web_max_instances=20"

# Upgrade database tier (for production)
terraform apply \
  -var="db_tier=db-n1-standard-2"
```

### Change Environment (e.g., dev to prod)

```bash
# Initialize new backend for prod
terraform init \
  -backend-config=bucket=MY_PROJECT-terraform \
  -backend-config=prefix=todo/prod \
  -reconfigure

# Deploy prod with HA enabled
terraform apply \
  -var="environment=prod" \
  -var="db_tier=db-n1-standard-2"
```

## Monitoring Deployment

### Cloud Run Services

```bash
# List Cloud Run services
gcloud run services list --region=us-central1

# View service details
gcloud run services describe todo-dev-web --region=us-central1

# View recent revisions
gcloud run revisions list --region=us-central1 --limit=10

# Stream logs
gcloud run services logs read todo-dev-web --region=us-central1 --follow
```

### Cloud SQL

```bash
# List Cloud SQL instances
gcloud sql instances list

# View instance details
gcloud sql instances describe todo-dev-postgres

# Check backups (prod only)
gcloud sql backups list --instance=todo-dev-postgres

# View database size
gcloud sql operations list --instance=todo-dev-postgres --limit=10
```

### Secret Manager

```bash
# List secrets
gcloud secrets list

# View secret metadata
gcloud secrets describe todo-dev-db-url

# Ensure service account has access
gcloud secrets get-iam-policy todo-dev-db-url
```

## Troubleshooting

### Cloud Run Service Not Starting

**Error:** `Service failed to become healthy`

```bash
# Check startup logs
gcloud run services logs read SERVICE_NAME --region=REGION --limit=100

# Common causes:
# - DATABASE_URL secret not accessible
# - Database not ready
# - Application crash (port not listening)

# Restart the service
gcloud run services update-traffic SERVICE_NAME --to-revisions LATEST=100
```

### Database Connection Fails

**Error:** `failed to connect to server`

```bash
# Verify Cloud SQL instance is running
gcloud sql instances describe INSTANCE_NAME

# Check service account permissions
gcloud sql instances describe INSTANCE_NAME --format='value(databaseVersion)'

# Verify VPC Access Connector
gcloud compute vpc-access connectors describe CONNECTOR_NAME --region=REGION
```

### Terraform State Conflicts

**Error:** `Error acquiring the state lock`

```bash
# View lock holders
gsutil cat gs://BUCKET/LOCK

# Force unlock (use with caution)
terraform force-unlock LOCK_ID
```

### Insufficient Permissions

**Error:** `Permission denied: Cloud SQL`

```bash
# Grant missing roles
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member=serviceAccount:SA_EMAIL \
  --role=roles/cloudsql.admin

# For each required role:
# - roles/cloudsql.admin
# - roles/secretmanager.admin
# - roles/compute.networkAdmin
# - roles/run.admin
```

## Cleanup

### Remove a Deployment

```bash
cd src/infrastructure

# See what will be deleted
terraform plan -destroy

# Destroy all resources (if not prod protected)
terraform destroy \
  -var="project_id=MY_PROJECT" \
  -var="api_image=..." \
  -var="web_image=..."
```

### Remove Terraform Backend

```bash
# Delete state bucket (contains all deployment history)
gsutil -m rm -r gs://MY_PROJECT-terraform
```

## Cost Management

### Estimate Costs

```bash
# Use Terraform cloud to estimate
# or use GCP pricing calculator
# Key cost drivers:
# - Cloud SQL instance size (per hour)
# - Cloud Run requests and CPU (per 100ms)
# - Data transfer (egress from GCP)
# - Storage (if using persistent volumes)
```

### Optimize for Lower Costs (Dev Only)

```bash
terraform apply \
  -var="environment=dev" \
  -var="db_tier=db-f1-micro" \
  -var="api_max_instances=1" \
  -var="web_max_instances=1"

# Services will scale to zero when not in use
# Only pay for requests and minimal database instance
```

## Next Steps

- Monitor your deployment with Cloud Console
- Set up continuous deployment (CD) in your CI/CD pipeline
- Implement automated backups (prod) and disaster recovery
- Configure custom domain with Cloud CDN
- Set up alerting and monitoring dashboards
