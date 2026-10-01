# Database

The database layer uses **PostgreSQL 17** with **node-pg-migrate** for schema versioning and migrations.

## Technology Stack

- **PostgreSQL 17** — Relational database
- **node-pg-migrate** — SQL migration tool
- **pg** — PostgreSQL client library

## Project Structure

```
src/db/
├── migrations/
│   ├── 1718500000000_initial-schema.js   # Users table
│   └── 1718500001000_create-tasks.js     # Tasks table
├── package.json
└── Dockerfile
```

## Schema

### Users Table

```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  created_at TIMESTAMP NOT NULL DEFAULT now()
);
```

**Migration:** `1718500000000_initial-schema.js`

Stores user accounts with email as unique identifier and automatic creation timestamp.

### Tasks Table

```sql
CREATE TABLE tasks (
  id SERIAL PRIMARY KEY,
  title VARCHAR(500) NOT NULL,
  completed BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMP NOT NULL DEFAULT now()
);
```

**Migration:** `1718500001000_create-tasks.js`

Stores task items with:
- `id` — Auto-incrementing primary key
- `title` — Task description (up to 500 characters)
- `completed` — Boolean flag (defaults to false)
- `created_at` — Automatic timestamp on insert

## Migrations

Migrations are managed with **node-pg-migrate**, which provides a programmatic API for defining schema changes.

### Migration Format

Each migration file exports `up` and `down` functions:

```javascript
exports.up = (pgm) => {
  pgm.createTable('table_name', { /* columns */ });
};

exports.down = (pgm) => {
  pgm.dropTable('table_name');
};
```

### Running Migrations

```bash
# Apply all pending migrations
cd src/db
DATABASE_URL=postgres://app:app@localhost:5432/app npx node-pg-migrate up

# Roll back the last migration
DATABASE_URL=postgres://app:app@localhost:5432/app npx node-pg-migrate down
```

npm scripts:

```bash
npm run migrate      # Apply all pending migrations
npm run migrate:down # Roll back last migration
```

### Automatic Migrations

In Docker Compose, the `migrate` service automatically runs migrations on startup:

```yaml
migrate:
  build:
    context: ./src/db
  environment:
    DATABASE_URL: postgres://app:app@postgres:5432/app
  depends_on:
    postgres:
      condition: service_healthy
```

## Environment Variables

```bash
DATABASE_URL=postgres://user:pass@host:5432/dbname  # PostgreSQL connection string
```

## Docker

The database migration container runs migrations during Docker Compose startup:

```dockerfile
# Dockerfile in src/db/
# - Uses node:22-alpine
# - Installs dependencies
# - Runs: node-pg-migrate up
# - Exits after completion
```

**Local PostgreSQL Service in Docker Compose:**

```yaml
postgres:
  image: postgres:17-alpine
  environment:
    POSTGRES_DB: app
    POSTGRES_USER: app
    POSTGRES_PASSWORD: app
  volumes:
    - postgres_data:/var/lib/postgresql/data
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U app -d app"]
    interval: 5s
    timeout: 5s
    retries: 5
```

## Connection String

**Local Development:**
```
postgres://app:app@localhost:5432/app
```

**Docker Compose (internal):**
```
postgres://app:app@postgres:5432/app
```

**Cloud SQL (Terraform-managed):**
```
postgres://app:PASSWORD@PRIVATE_IP:5432/app
```

The connection string is stored in Google Secret Manager during cloud deployment.

## Data Persistence

### Local Development

Docker Compose creates a named volume `postgres_data` to persist data between container restarts:

```bash
# Stop containers (keeps data)
docker compose down

# Stop and delete all data
docker compose down -v
```

### Cloud Deployment

Cloud SQL automatically manages:
- **Automatic backups** (enabled in prod environment)
- **High availability** (Regional replication in prod)
- **Disk auto-resize** (automatically increases storage as needed)
- **Point-in-time recovery** (configurable retention)

## Deployment

On Google Cloud Platform, the database is provisioned by Terraform with:

- **Cloud SQL PostgreSQL 17** instance
- **Private IP only** (accessible only from VPC)
- **VPC Access Connector** for Cloud Run integration
- **Automatic backups** (prod only)
- **High availability** (prod: Regional, dev: Zonal)
- **app** user with auto-generated password stored in Secret Manager

See [Infrastructure](infrastructure.md) for more details.
