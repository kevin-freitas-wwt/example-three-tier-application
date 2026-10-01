# API

The backend is an **Express 5** REST API that handles task management operations, with a PostgreSQL database connection pool for data persistence.

## Technology Stack

- **Express 5** — Minimal web framework
- **Node.js 22** — JavaScript runtime
- **pg** — PostgreSQL client
- **Built-in modules** — no external middleware dependencies

## Project Structure

```
src/api/
├── index.js        # Express app, route handlers, middleware
├── db.js           # PostgreSQL connection pool
├── package.json
├── Dockerfile
└── test/           # Test files (Node.js native test runner)
```

## Core Files

### `index.js` — Express Server

Exports an Express application with the following structure:

- **JSON middleware** — `app.use(express.json())`
- **Health check endpoint** — `/health` for monitoring
- **Task endpoints** — CRUD operations on tasks
- **Error handling** — HTTP status codes and error messages
- **Port configuration** — Reads `PORT` environment variable (default: 3001)

### `db.js` — PostgreSQL Connection

```javascript
const { Pool } = require('pg');
const pool = new Pool({ connectionString: process.env.DATABASE_URL });
module.exports = pool;
```

Creates a single connection pool from the `DATABASE_URL` environment variable, reused across all requests.

## API Endpoints

### Health Check

```
GET /health
```

Returns `{ "status": "ok" }` for monitoring and liveness probes.

### List Tasks

```
GET /tasks
```

Returns all tasks, ordered by creation time (ascending).

**Response:**
```json
[
  {
    "id": 1,
    "title": "Buy groceries",
    "completed": false,
    "created_at": "2025-01-15T10:30:00Z"
  }
]
```

### Create Task

```
POST /tasks
Content-Type: application/json

{ "title": "New task title" }
```

Creates a new task with the provided title.

**Validation:**
- `title` is required
- Must be a non-empty string
- Whitespace is trimmed

**Response (201 Created):**
```json
{
  "id": 1,
  "title": "New task title",
  "completed": false,
  "created_at": "2025-01-15T10:30:00Z"
}
```

**Error (400 Bad Request):**
```json
{ "error": "title is required" }
```

### Update Task

```
PATCH /tasks/:id
Content-Type: application/json

{ "completed": true }
```

or

```json
{ "title": "Updated title" }
```

or both:

```json
{ "completed": true, "title": "Updated title" }
```

Updates the task completion status and/or title. Omitted fields retain their current values.

**Response:**
```json
{
  "id": 1,
  "title": "Updated title",
  "completed": true,
  "created_at": "2025-01-15T10:30:00Z"
}
```

**Error (404 Not Found):**
```json
{ "error": "Not found" }
```

## Environment Variables

```bash
PORT=3001              # Server port (default: 3001)
DATABASE_URL=postgres://user:pass@host:5432/dbname  # PostgreSQL connection string
```

## Running Locally

### Development Mode

```bash
npm run dev
```

Starts the server with auto-reload via `node --watch`.

### Production Mode

```bash
npm start
```

Starts the server with `node index.js`.

### Running Tests

```bash
npm test
```

Uses Node.js native test runner (`node --test`).

## Dependencies

- **express** (^5.2.1) — Web framework
- **pg** (^8.21.0) — PostgreSQL client

## Docker

The API runs in a Docker container as part of the multi-container application:

```dockerfile
# Dockerfile
# - Uses node:22-alpine as base image
# - Installs dependencies with npm ci
# - Exposes port 3001 internally
# - Starts with npm start
```

**Environment in Docker Compose:**

```yaml
environment:
  PORT: 3001
  DATABASE_URL: postgres://app:app@postgres:5432/app
```

## Error Handling

The API returns appropriate HTTP status codes:

- **200 OK** — Successful GET or PATCH
- **201 Created** — Successful POST
- **400 Bad Request** — Invalid input (missing/invalid title)
- **404 Not Found** — Task ID does not exist
- **500 Internal Server Error** — Database or server errors (not explicitly handled, Express default)

## Database Connection

The API uses a single `pg.Pool` instance for all database operations. The pool:

- Maintains a connection queue
- Auto-manages connection reuse
- Can be configured via environment variables (idle timeout, max connections, etc.)
- Is initialized once on module load

## Deployment

The API is deployed to **Google Cloud Run** with Terraform, configured to:

- Run with 1 CPU and 512 MB memory per instance
- Scale from 0 (dev) or 1 (prod) to 10 instances
- Use a startup probe (`GET /health`) to wait for readiness
- Use a liveness probe to detect unhealthy instances
- Connect to Cloud SQL via VPC Access Connector
- Access the database URL from Secret Manager
