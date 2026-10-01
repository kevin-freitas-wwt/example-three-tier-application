# Known Issues

Known bugs, gaps, and risks found by reading the code. Each entry gives the **impact**, where it is, and a suggested fix. Remove an entry when it's fixed, or update it if it's partly addressed.

Severity levels:
- 🔴 High: a production or correctness bug
- 🟠 Medium: a robustness or security gap
- 🟢 Low: tech debt or a missing feature

---

## 🔴 Web → API calls on Cloud Run are likely to be rejected

- **Where:** `src/infrastructure/main.tf`, `src/web/app/actions.ts`
- **Details:** The API service has `ingress = INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER` and requires IAM `roles/run.invoker`. Three things go wrong with that setup:
  - The web service gets `API_URL = google_cloud_run_v2_service.api.uri`, which is the public `*.run.app` URL.
  - The web service uses VPC egress `PRIVATE_RANGES_ONLY`, so calls to that URL don't go through the VPC.
  - `fetch` in `actions.ts` doesn't attach a Google-signed ID token.

  Either the ingress rule or the IAM check is likely to reject the request (404/403), so the page won't render.
- **Fix:** Do both of the following:
  - Use `INGRESS_TRAFFIC_INTERNAL_ONLY` with web egress `ALL_TRAFFIC`, or put an internal load balancer in front of the API.
  - Have the web tier fetch an ID token from the metadata server for the API audience and send it as `Authorization: Bearer`.

## 🔴 The new API revision deploys before migrations run

- **Where:** `.github/workflows/deploy.yml`
- **Details:** `terraform apply` rolls out the new API image first, and the `migrate` job runs afterwards. A release that depends on a new column will fail until the migration finishes. If the migration fails, the new code stays live against the old schema.
- **Fix:** Run the migration job before the Cloud Run services update. One option is two-phase Terraform: apply the job, run it, then apply the services. Alternatively, keep migrations backward-compatible (expand/contract).

## 🟠 API has no error handling middleware

- **Where:** `src/api/index.js`, `src/api/db.js`
- **Details:**
  - Database errors bubble up to Express's default handler. It returns an HTML 500 and logs the stack, not the `{ error }` JSON the rest of the API uses.
  - The `pg.Pool` has no `'error'` listener, so an error on an idle client (for example, a database restart) can crash the process.
- **Fix:** Add a final `app.use((err, req, res, next) => ...)` that returns JSON, and add `pool.on('error', ...)`.

## 🟠 Input validation gaps on `PATCH /tasks/:id` and `POST /tasks`

- **Where:** `src/api/index.js`
- **Details:**
  - A non-numeric `:id` becomes `NaN` and is sent to Postgres, which causes a 500 instead of a 400/404.
  - A non-string `title` on PATCH throws a `TypeError` on `.trim()` (500).
  - An empty or whitespace-only title is accepted on PATCH.
  - A title longer than 500 characters isn't checked, so it fails the `varchar(500)` constraint with a 500. `agents.md` suggests a 200-character limit with `422`.
  - PATCH does a read and then a write in separate queries, so it isn't atomic.
- **Fix:**
  - Validate the id and the body up front, reusing the POST rules for `title`.
  - Return 400/422 for bad input.
  - Replace the two queries with one `UPDATE ... SET col = COALESCE($n, col) ... RETURNING *` and return 404 when no row is updated.

## 🟠 The web tier ignores API failures on mutations

- **Where:** `src/web/app/actions.ts`, `src/web/app/page.tsx`
- **Details:**
  - `createTask` and `toggleTask` don't check `res.ok`, so failures are silently ignored.
  - `getTasks` throws when the API is down. There is no `error.tsx` boundary, so the user sees the generic Next.js error page.
  - The Cloud Run startup probe for web hits `/`, which calls the API. If the API is unavailable, new web revisions fail to start.
- **Fix:**
  - Check `res.ok` and show errors to the user (for example, return state for `useActionState`).
  - Add `app/error.tsx`.
  - Point the web startup probe at a static route that doesn't call the API.

## 🟠 Toggle uses render-time state

- **Where:** `src/web/app/page.tsx`
- **Details:** The toggle sends `!task.completed` using the value from when the page was rendered. If the page is stale (for example, open in two tabs), it can set the wrong value instead of flipping the current one.
- **Fix:** Add an explicit toggle endpoint, or send the intended value from a checkbox's actual state.

## 🟠 Secrets and credentials

- The database password and the full `DATABASE_URL` are stored in Terraform state (`random_password`, `secret_data`). The GCS state bucket must be locked down.
- Docker Compose uses hardcoded `app/app` credentials. That's fine for local use, but never reuse them.
- `deploy.yml` runs `terraform apply -auto-approve` on every push to `main` with no plan review.

## 🟢 Container Registry (`gcr.io`) is deprecated

- **Where:** `.github/workflows/deploy.yml`, README
- **Details:** Images are pushed to `gcr.io`, but Google has deprecated Container Registry in favour of Artifact Registry. The workflow also pushes mutable `:latest` tags next to the `:<sha>` tags.
- **Fix:** Move to Artifact Registry (`<region>-docker.pkg.dev/...`) and deploy only immutable SHA tags.

## 🟢 Missing features and tech debt

- There's no `DELETE /tasks/:id` endpoint and no delete button in the UI.
- The `users` table (initial migration) isn't used anywhere, and there is no authentication or authorization.
- `created_at` columns are `timestamp` without a time zone. Prefer `timestamptz` in new migrations.
- `GET /tasks` returns every row with no pagination.
- Test coverage is minimal:
  - The only API test is `/health`.
  - There are no web tests.
  - Migrations are only syntax-checked in CI and never applied to a real Postgres.
  - The `src/db` `npm test` script is a placeholder that always fails.
- There's no `.env.example` documenting `DATABASE_URL`, `PORT`, and `API_URL`.
- `forge-wiki/` at the repo root holds older generated docs that overlap with this wiki. Consolidate them or remove one of them.
