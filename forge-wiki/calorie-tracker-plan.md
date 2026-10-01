# Calorie Tracker: Plan and PR Breakdown

## Goal

Add a simple calorie tracking feature to the existing three-tier to-do app
(`src/db` → `src/api` → `src/web`), following the same patterns already used
for tasks.

A user can:
- Log a food entry (name + calories) for "today".
- See a list of today's food entries and a running calorie total.
- Delete a food entry.

## Why split this way

The project's own guidance (`agents.md`, "Scope changes to one tier at a
time") says to do migration, then API, then frontend, verifying each layer
before moving to the next. This plan follows that seam, which also happens to
match natural pull-request boundaries: each PR is independently buildable and
testable by CI (`web`, `api`, `db` jobs in `.github/workflows/ci.yml`).

## PR 1 — Database: `food_entries` table

- New `node-pg-migrate` migration (append-only, per `agents.md`) adding a
  `food_entries` table: `id`, `name` (varchar), `calories` (integer, > 0),
  `logged_at` (timestamp, defaults to `now()`).
- No API or web changes.
- Verified with: `node --check` over the new migration file (same check CI
  runs for `src/db`).

## PR 2 — API: food entry routes

- `GET /food-entries` — list entries, newest first.
- `POST /food-entries` — create an entry (`name`, `calories`), with basic
  validation (name required, calories a positive number).
- `DELETE /food-entries/:id` — remove an entry, 404 if missing.
- Reuses the existing `src/api/db.js` pool, same style as the `tasks` routes
  in `src/api/index.js`.
- Verified with: `node --check index.js db.js` and the existing smoke test
  (`npm test`); manual `curl` against `docker compose up` per the Known
  Issues note that CI's smoke test doesn't exercise real DB access.

## PR 3 — Web: calorie tracker page

- New route `src/web/app/calories/page.tsx` plus `src/web/app/calories/actions.ts`
  (server actions calling the API), mirroring `app/actions.ts` / `app/page.tsx`
  for tasks.
- Form to add an entry, list of today's entries with a delete button, and a
  running total of calories.
- Verified with: `npm run lint` and `npm run build` in `src/web` (same checks
  CI's `web` job runs).

## PR 4 — Wrap-up

- Link the new page from the home page nav (small, low-risk change).
- Final full build/lint pass across all three tiers, open the PR for human
  review. No auto-merge.

## Notes

- Because this work happens in a single agent session, all four PRs above
  are implemented as separate, reviewable commits on one branch/pull
  request rather than four separate GitHub PRs — the branch cannot be split
  after the fact without losing that structure. Each commit corresponds 1:1
  to a PR above and leaves the repo in a working, independently buildable
  state.
