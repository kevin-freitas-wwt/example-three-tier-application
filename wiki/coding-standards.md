# Coding Standards

Conventions for `example-three-tier-application`, taken from the code, `agents.md`, and CI (`.github/workflows/ci.yml`). Where this page and the code disagree, the code wins. Please fix the page.

## General

- **Runtime versions are pinned:** use Node.js 22 (`node:22-alpine` in every Dockerfile, `node-version: 22` in CI) and PostgreSQL 17 (`postgres:17-alpine` locally, `POSTGRES_17` on Cloud SQL). Match these versions in any new Dockerfile or dependency.
- **Configuration comes from environment variables.** Connection strings, ports, and service URLs are passed in as env vars (`DATABASE_URL`, `PORT`, `API_URL`). Don't hardcode environment-specific values. The local fallbacks (`PORT || 3001`, `API_URL || 'http://localhost:3001'`) are only for development.
- **Each tier is its own npm package** (`src/api`, `src/db`, `src/web`) with its own `package-lock.json`. Install with `npm ci`, and commit lockfile changes.
- **Change one tier at a time.** For a feature that touches every tier, do the migration first, then the API, then the frontend, and check each step before moving on (`agents.md`).

## API (`src/api`, Express 5, CommonJS)

- Use CommonJS (`require` / `module.exports`). `package.json` sets `"type": "commonjs"`.
- Put route handlers in `index.js`. Each route gets a short comment in the form `// METHOD /path — description`.
- Keep the shared `pg` `Pool` in `db.js`. Import it and call `db.query(...)`. Don't create a new client for each request.
- **Always use parameterized SQL** (`$1, $2, ...` with a values array). Never build SQL by joining strings.
- Validate request bodies at the top of the handler and return JSON errors in the form `{ error: '<message>' }`:
  - `400` for invalid input, `404` for a missing resource, `201` with the created row for a POST.
- Return database rows directly as JSON. Use `RETURNING *` on INSERT/UPDATE so you don't need a second query.
- Handlers are `async`. Express 5 forwards rejected promises to the error handler, so you don't need `try/catch` in every route. There is no custom error middleware yet (see [known-issues.md](known-issues.md)).
- Keep `GET /health` working without a database connection. The smoke test and the Cloud Run probes depend on it.

## Database migrations (`src/db`, node-pg-migrate)

- **Migrations are append-only.** Never edit a migration that has been merged. Add a new one instead.
- File names follow `<millisecond-timestamp>_<kebab-description>.js`, for example `1718500001000_create-tasks.js`.
- Each file exports `up` and `down`, written with the `pgm` builder (`pgm.createTable`, `pgm.func('now()')`, ...). `down` must undo `up` completely.
- Table conventions so far: `id serial primary key`, `created_at timestamp not null default now()`, and `notNull` on required columns.

## Web (`src/web`, Next.js 16 App Router, TypeScript, Tailwind 4)

- **Read `src/web/AGENTS.md` first.** Next.js 16 has breaking changes. Check `node_modules/next/dist/docs/` before relying on APIs you remember from older versions.
- Only server code talks to the API. Put data access in `app/actions.ts` (`'use server'`) and use `API_URL`, which is never exposed to the browser. Components call these actions. The browser never calls the API directly.
- Call `revalidatePath('/')` after a mutation so the server-rendered page refreshes.
- Put shared types (for example `Task`) next to the actions that return them.
- Style with Tailwind utility classes. Use the `zinc` palette and add a `dark:` variant for every colour.
- Use semantic HTML with `aria-label` on icon-only buttons.
- `next.config.ts` uses `output: "standalone"`. The Dockerfile depends on this, so don't remove it.
- Linting uses `eslint-config-next` (core-web-vitals and typescript). `npm run lint` must pass.

## Infrastructure (`src/infrastructure`, Terraform ≥ 1.5, google ~> 5.0)

- Name every resource with the `local.name_prefix` prefix (`${app_name}-${environment}`), for example `todo-dev-api`. CI depends on this pattern to find the migration job.
- Set environment-dependent behaviour with `var.environment == "prod" ? ... : ...` (HA, backups, deletion protection, min instances).
- Store secrets in Secret Manager and inject them through `secret_key_ref`. Never put them in plain `env` values.
- The backend has no hardcoded values. Pass the bucket and prefix through `-backend-config`.
- Add new variables to `variables.tf` with a `description`, and add `validation` where the set of values is fixed.

## Testing and CI

- API tests use the built-in `node:test` runner (`npm test`, files in `src/api/test/`). They start the real server on a free port. Use `node:assert/strict`.
- CI must pass before merging:
  - **web:** lint and build.
  - **api:** `node --check` and the smoke tests.
  - **db:** `node --check` on every migration.
- CI steps are wrapped in `.github/scripts/run-step.sh`, which shortens the logs and reports failures in the step summary. Wrap new steps the same way.
