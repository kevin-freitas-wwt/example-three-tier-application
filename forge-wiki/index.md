# Example Three-Tier Application

A reference implementation of a three-tier web application demonstrating modern full-stack development with Next.js, Express, and PostgreSQL. The application runs locally with Docker Compose and deploys to Google Cloud Platform (Cloud Run + Cloud SQL) via Terraform.

## Application Overview

The example is a **task manager (to-do list)** that showcases how the three tiers communicate:

```
Browser → Web (Next.js :3000) → API (Express :3001) → PostgreSQL
```

## Architecture Layers

| Layer | Technology | Location |
|-------|-----------|----------|
| **Frontend** | Next.js 16, React 19, Tailwind CSS | `src/web/` |
| **API** | Express 5, Node.js 22 | `src/api/` |
| **Database** | PostgreSQL 17 | `src/db/` |
| **Migrations** | node-pg-migrate | `src/db/migrations/` |
| **Infrastructure** | Terraform (GCP) | `src/infrastructure/` |

## Key Features

- **Server-side rendering** with Next.js App Router and Server Actions
- **RESTful API** endpoints for task management
- **Database schema** managed with migrations
- **Docker Compose** for local development
- **Terraform** Infrastructure as Code for GCP deployment
- **Dark mode support** with Tailwind CSS

## Documentation

- [**Frontend**](frontend.md) — Next.js, React, and the UI
- [**API**](api.md) — Express REST API endpoints and middleware
- [**Database**](database.md) — PostgreSQL schema and migrations
- [**Infrastructure**](infrastructure.md) — Terraform, VPC, Cloud SQL, and Cloud Run
- [**Local Development**](local-development.md) — Running with Docker Compose
- [**Deployment**](deployment.md) — Deploying to Google Cloud Platform

## Quick Start

### Local Development

```bash
docker compose up --build
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Deploy to GCP

```bash
cd src/infrastructure
terraform init
terraform apply \
  -var="project_id=my-project" \
  -var="api_image=gcr.io/my-project/api:latest" \
  -var="web_image=gcr.io/my-project/web:latest"
```

## Project Structure

```
src/
├── api/            # Express REST API
│   ├── index.js    # Route handlers and middleware
│   ├── db.js       # PostgreSQL connection pool
│   └── Dockerfile
├── db/             # Database layer
│   ├── migrations/ # node-pg-migrate migration files
│   └── Dockerfile
├── web/            # Next.js frontend
│   ├── app/        # App Router pages and components
│   └── Dockerfile
└── infrastructure/ # Terraform configuration
    ├── main.tf     # Core resources (VPC, Cloud SQL, Cloud Run)
    ├── variables.tf
    └── outputs.tf
```

## Technology Stack

### Frontend
- **Next.js 16** — React meta-framework with server-side rendering
- **React 19** — UI library
- **Tailwind CSS 4** — Utility-first CSS framework
- **TypeScript** — Type safety

### Backend
- **Express 5** — Minimal web framework
- **Node.js 22** — JavaScript runtime
- **pg** — PostgreSQL client library

### Database
- **PostgreSQL 17** — Relational database
- **node-pg-migrate** — SQL migration tool

### Infrastructure
- **Docker & Docker Compose** — Containerization and orchestration
- **Terraform** — Infrastructure as Code
- **Google Cloud Platform** — Cloud hosting

## License

See LICENSE file for details.
