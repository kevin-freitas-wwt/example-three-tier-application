# Architecture Decisions

Lightweight decision records for `example-three-tier-application`, worked out from the code. Each entry gives the context, the decision, and its consequences. Add new decisions at the end, and mark replaced ones **Superseded** instead of deleting them.

---

## ADR-001: Three separate tiers (web → API → database)

- **Status:** Accepted
- **Context:** The repo is a reference implementation showing how the tiers of a classic web app talk to each other.
- **Decision:**
  - The browser reaches only the **Next.js web tier** (`src/web`).
  - The web tier calls the **Express REST API** (`src/api`) over HTTP.
  - Only the API connects to **PostgreSQL**.
- **Consequences:**
  - The layers are clearly separated and each one deploys on its own.
  - Every request goes through an extra network hop.
  - Each tier has its own package, Dockerfile, and CI job.

## ADR-002: The API is internal-only

- **Status:** Accepted
- **Context:** Exposing the API directly would widen the attack surface and require CORS and authentication in two places.
- **Decision:**
  - In Docker Compose, the API uses `expose: 3001` and no host port is mapped.
  - On GCP, the API's Cloud Run service uses `ingress = INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER`, and `roles/run.invoker` is granted only to the app service account.
  - The web service is public (`allUsers` invoker).
- **Consequences:**
  - All external traffic goes through the web tier's server-side code.
  - To debug the API locally, you have to map a port temporarily.

## ADR-003: Next.js App Router with Server Actions as the API client

- **Status:** Accepted
- **Context:** The frontend needs data from an API the browser can't reach (ADR-002).
- **Decision:**
  - Pages are async Server Components.
  - Mutations and fetches live in `app/actions.ts` (`'use server'`), which call `API_URL` and then `revalidatePath('/')`.
  - The fetch uses `cache: 'no-store'`.
- **Consequences:**
  - No client-side JavaScript is needed for data access, and the forms work through progressive enhancement.
  - Every interaction re-renders the page on the server.
  - There are no optimistic updates.

## ADR-004: Schema managed by node-pg-migrate in a dedicated migration image

- **Status:** Accepted
- **Context:** The schema has to be applied in the same way locally and in the cloud, before the API starts.
- **Decision:**
  - Migrations live in `src/db/migrations` and are packaged as their own image, which runs `node-pg-migrate up`.
  - Locally, a Compose `migrate` service runs after Postgres is healthy. The API waits for it with `service_completed_successfully`.
  - On GCP, a Cloud Run Job (`<prefix>-migrate`, `migration.tf`) is run by the deploy workflow.
  - Migrations are append-only.
- **Consequences:**
  - The same artifact applies the schema everywhere.
  - The deploy order is images → Terraform → migrations. Because of this order, a new API revision can briefly run against the old schema (see [known-issues.md](known-issues.md)).

## ADR-005: Plain `pg` pool, no ORM

- **Status:** Accepted
- **Decision:** The API uses one shared `pg.Pool` (`db.js`), configured only by `DATABASE_URL`, and runs hand-written parameterized SQL.
- **Consequences:**
  - There are few dependencies and the SQL is easy to read.
  - The API doesn't get type safety for rows. Schema changes need manual updates to the API and to the `Task` type in the web tier.

## ADR-006: GCP deployment on Cloud Run + Cloud SQL via Terraform

- **Status:** Accepted
- **Decision:** Terraform in `src/infrastructure` provisions:
  - a custom VPC and subnet
  - private services access and a Cloud SQL Postgres 17 instance with private IP only (no public IPv4)
  - a Serverless VPC Access connector
  - Cloud Run v2 services for the API and web, and a Cloud Run Job for migrations
  - one service account, with access to Cloud SQL as a client and to the secret
  - Secret Manager holding `DATABASE_URL`, built from a `random_password`

  State is stored in GCS, and the bucket and prefix are supplied at init time.
- **Consequences:**
  - The database is never reachable from the internet.
  - The connector adds a fixed cost (at least 2 `e2-micro` instances).
  - Production behaviour comes from `environment == "prod"`: REGIONAL HA, backups, deletion protection, and `min_instances=1`.

## ADR-007: One Terraform configuration, environments chosen by variable

- **Status:** Accepted
- **Decision:**
  - The `environment` variable (`dev` | `staging` | `prod`, with validation) drives resource names (`${app_name}-${environment}-*`) and production-only settings.
  - Each environment gets its own state prefix (`terraform/<env>`).
- **Consequences:**
  - There's no duplicated configuration.
  - All environments share the same structure, so differences have to be written as conditionals.

## ADR-008: CI/CD on GitHub Actions with Workload Identity Federation

- **Status:** Accepted
- **Decision:**
  - `ci.yml` runs on PRs and on pushes to `main`. It lints and builds web, syntax-checks and smoke-tests the API, and syntax-checks the migrations.
  - `deploy.yml` runs on pushes to `main` (default env `dev`) or manually through `workflow_dispatch`. It builds and pushes `api`, `web`, and `db` images to GCR, tagged `:<sha>` and `:latest`, then runs `terraform plan`/`apply -auto-approve`, then executes the migration job.
  - GCP authentication uses Workload Identity Federation, so no long-lived keys are stored.
- **Consequences:**
  - There are no stored service-account keys.
  - Every merge to `main` deploys `dev` automatically, with no human approval of the plan.
