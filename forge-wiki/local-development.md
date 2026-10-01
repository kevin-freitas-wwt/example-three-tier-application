# Local Development

This guide explains how to run the complete three-tier application locally using **Docker Compose**.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Docker Engine and Compose plugin)
- Or: [Docker Engine](https://docs.docker.com/engine/install/) + [Docker Compose plugin](https://docs.docker.com/compose/install/)

## Getting Started

### Start the Application Stack

```bash
docker compose up --build
```

This command:
1. Builds images for all services
2. Starts four containers in dependency order
3. Outputs logs from all services

**Expected startup sequence:**

1. **postgres** — PostgreSQL database starts and waits for health check
2. **migrate** — Database migrations run, then container exits
3. **api** — Express API starts on port 3001 (internal only)
4. **web** — Next.js frontend starts on port 3000

Once all services are running, open [http://localhost:3000](http://localhost:3000) in your browser.

### Docker Compose Services

**postgres** — PostgreSQL 17 database
- **Image:** `postgres:17-alpine`
- **Port:** 5432 (internal only)
- **Username:** app
- **Password:** app
- **Database:** app
- **Persistence:** `postgres_data` volume (survives container restart)

**migrate** — Database schema setup
- **Image:** Built from `src/db/Dockerfile`
- **Purpose:** Runs `node-pg-migrate up` on startup
- **Exit behavior:** Exits after migrations complete (doesn't run continuously)

**api** — Express REST API
- **Image:** Built from `src/api/Dockerfile`
- **Port:** 3001 (not exposed to host, only internal)
- **Depends on:** migrate (waits for completion)
- **Environment:**
  - `PORT=3001`
  - `DATABASE_URL=postgres://app:app@postgres:5432/app`

**web** — Next.js frontend
- **Image:** Built from `src/web/Dockerfile`
- **Port:** 3000 (exposed to host at http://localhost:3000)
- **Depends on:** api (waits for startup)
- **Environment:**
  - `PORT=3000`
  - `API_URL=http://api:3001`

## Common Commands

### View Logs

```bash
# Follow all service logs
docker compose logs -f

# Follow logs from specific service
docker compose logs -f web
docker compose logs -f api
docker compose logs -f postgres

# View last 50 lines
docker compose logs --tail=50
```

### Stop and Start

```bash
# Gracefully stop all containers (keeps postgres_data volume)
docker compose down

# Stop containers and delete all data (including database)
docker compose down -v

# Start previously built containers (no rebuild)
docker compose up

# Start in background (detached mode)
docker compose up -d
```

### Rebuild After Code Changes

```bash
# Rebuild and restart all services
docker compose up --build

# Rebuild specific service
docker compose build web
docker compose build api

# Build without starting
docker compose build
```

### Execute Commands in Containers

```bash
# Run a command in the api service
docker compose exec api npm test

# Open a shell in the postgres container
docker compose exec postgres psql -U app -d app

# Run a command in the web container
docker compose exec web npm run lint
```

### Reset Database

```bash
# Stop everything and delete postgres_data volume
docker compose down -v

# Start fresh with migrations applied
docker compose up --build
```

## Database Access

### From Host Machine

PostgreSQL is not exposed to the host. To access it:

```bash
# Use the postgres container
docker compose exec postgres psql -U app -d app

# Or temporarily expose the port
docker compose exec postgres psql -U app -d app -c "SELECT * FROM tasks;"
```

### From Inside Containers

Services inside Docker Compose can connect to postgres via the hostname `postgres`:

```
postgres://app:app@postgres:5432/app
```

## Troubleshooting

### Postgres Not Starting

**Error:** `postgres: FATAL: could not create shared memory segment`

**Solution:** Increase Docker's memory limit in Docker Desktop settings:
- Settings → Resources → Memory: increase to at least 4GB

### Port Already in Use

**Error:** `bind: address already in use`

**Solution:** Change the port mapping in `docker-compose.yml`:

```yaml
web:
  ports:
    - "3001:3000"  # Map host 3001 to container 3000
```

Then access the app at `http://localhost:3001`.

### Migrations Failed

**Error:** `migrate service exited with code 1`

**Solution:** 

```bash
# View migrate logs
docker compose logs migrate

# Reset database and retry
docker compose down -v
docker compose up --build
```

### API Not Responding

**Error:** Web shows "Failed to fetch" errors

**Solution:**

```bash
# Check API logs
docker compose logs api

# Restart API
docker compose restart api

# Or rebuild completely
docker compose down -v
docker compose up --build
```

### Stale Node Modules

**Error:** `Module not found` or `Cannot find package`

**Solution:**

```bash
# Force rebuild all images (don't use cached layers)
docker compose build --no-cache

# Start with fresh build
docker compose up --build
```

## Development Workflow

### Edit Frontend Code

```bash
# 1. Make changes to src/web/app/
# 2. Next.js hot-reload automatically updates
# 3. Refresh browser to see changes
```

### Edit API Code

```bash
# 1. Make changes to src/api/index.js
# 2. The API restarts automatically (node --watch)
# 3. Test with curl or the frontend UI
```

### Add Database Migration

```bash
# 1. Create new migration file in src/db/migrations/
# 2. Restart Docker Compose
docker compose down -v
docker compose up --build

# Or run migration manually
docker compose exec migrate npx node-pg-migrate up
```

### Run API Tests

```bash
docker compose exec api npm test
```

### Run Frontend Linter

```bash
docker compose exec web npm run lint
```

## Performance Tips

### Use Detached Mode

```bash
# Start in background
docker compose up -d

# View logs when needed
docker compose logs -f
```

### Skip Build When Source Unchanged

```bash
# Reuse existing images
docker compose up

# Don't rebuild unless explicitly requested
docker compose up --no-build
```

### Limit Log Output

```bash
# Only follow specific service
docker compose logs -f api

# Show last N lines
docker compose logs --tail=20 web
```

## Next Steps

- Read [Frontend](frontend.md) to understand the Next.js application
- Read [API](api.md) to understand the Express endpoints
- Read [Database](database.md) to understand migrations and schema
- Read [Deployment](deployment.md) to deploy to Google Cloud Platform
