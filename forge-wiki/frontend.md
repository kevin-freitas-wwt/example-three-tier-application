# Frontend

The frontend is a **Next.js 16** application using the **App Router**, **React Server Components**, and **Server Actions** for seamless server-side data fetching and mutations.

## Technology Stack

- **Next.js 16** — React meta-framework with built-in server-side rendering
- **React 19** — UI component library
- **Tailwind CSS 4** — Utility-first styling
- **TypeScript** — Type-safe development

## Project Structure

```
src/web/
├── app/
│   ├── layout.tsx      # Root layout with metadata and dark mode support
│   ├── page.tsx        # Home page — Server Component, fetches tasks
│   ├── TaskList.tsx    # Client Component — all interactive UI
│   ├── actions.ts      # Server Actions for API calls
│   ├── globals.css     # Tailwind CSS configuration
│   └── favicon.ico
├── public/             # Static assets
├── package.json
├── tsconfig.json
├── next.config.ts
├── postcss.config.mjs  # PostCSS with Tailwind
└── eslint.config.mjs
```

## Features

### Server Components and Server Actions

The frontend uses **Next.js Server Actions** to handle data fetching and mutations directly in React components without traditional API endpoints on the frontend.

#### `app/actions.ts`

Exports async functions that fetch from the backend API:

```typescript
getTasks(): Promise<Task[]>                              // Fetch all tasks
createTask(formData: FormData)                           // Create a new task
toggleTask(id: number, completed: boolean)               // Update completion status
deleteTask(id: number): Promise<void>                    // Delete a task
updateTaskTitle(id: number, title: string,               // Rename a task
                originalTitle: string): Promise<void>
```

`updateTaskTitle` skips the network call if the trimmed title is empty or identical to the original.

After each mutation, `revalidatePath('/')` refreshes the page data.

#### `app/page.tsx`

A minimal **Server Component** that:
- Fetches all tasks server-side with `getTasks()`
- Passes them to `<TaskList initialTasks={tasks} />` as props

#### `app/TaskList.tsx` — Client Component

`'use client'` component that owns all interactive state:

| Feature | Implementation |
|---------|---------------|
| **Optimistic add** | `useOptimistic` shows a faded pending row immediately on submit; input clears before the server round-trip completes |
| **Filter tabs** | All / Active / Completed pill buttons; active tab has a filled background; tabs are hidden when the list is empty |
| **Delete button** | `×` button on each row; calls `deleteTask` inside `startTransition`; turns red on hover |
| **Inline edit** | Clicking a non-completed task title renders a focused `<input>`; Enter or blur commits; Escape cancels |
| **Keyboard focus ring** | Checkbox button uses `focus-visible:ring-2 focus-visible:ring-zinc-500 focus-visible:ring-offset-2` |
| **Empty-state illustration** | 📋 emoji + message shown when `visibleTasks.length === 0` (respects active filter) |

### App Metadata

`app/layout.tsx` exports:
```typescript
export const metadata: Metadata = {
  title: 'To-Do List',
  description: 'A simple task manager.',
};
```

### Styling

- **Tailwind CSS 4** for styling
- **Dark mode support** via `dark:` class variants
- **Responsive design** with mobile-first approach
- **Accessible UI** with semantic HTML, ARIA labels, and visible focus rings

### Environment Variables

```bash
API_URL=http://api:3001  # Backend API base URL (default: http://localhost:3001)
PORT=3000                 # Port to listen on (default: 3000)
```

## Running Locally

### Development Mode

```bash
npm run dev
```

Starts Next.js dev server with hot-reload on [http://localhost:3000](http://localhost:3000).

### Production Build

```bash
npm run build
npm start
```

Builds and starts the production server.

### Linting

```bash
npm run lint
```

Runs ESLint to check for code issues.

## Dependencies

- **next** (16.2.9) — React framework
- **react** (19.2.4) — UI library
- **react-dom** (19.2.4) — DOM rendering

### Dev Dependencies

- **@tailwindcss/postcss** (^4) — Tailwind CSS
- **tailwindcss** (^4) — CSS framework
- **typescript** (^5) — Type checking
- **eslint** (^9) — Code linting
- **@types/react** (^19) — React type definitions

## Docker

The frontend runs in a Docker container as part of the multi-container application:

```dockerfile
# Dockerfile builds a Next.js application
# - Uses node:22-alpine as base image
# - Installs dependencies with npm ci
# - Builds the application with npm run build
# - Starts with npm start
```

## API Integration

The frontend communicates with the backend API via `process.env.API_URL`. Server Actions handle all HTTP requests:

```typescript
const API_URL = process.env.API_URL || 'http://localhost:3001';

// GET /tasks
const tasks = await fetch(`${API_URL}/tasks`).then(r => r.json());

// POST /tasks
await fetch(`${API_URL}/tasks`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ title })
});

// PATCH /tasks/:id  (toggle or rename)
await fetch(`${API_URL}/tasks/${id}`, {
  method: 'PATCH',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ completed })   // or { title }
});

// DELETE /tasks/:id
await fetch(`${API_URL}/tasks/${id}`, { method: 'DELETE' });
```

## Deployment

The frontend is deployed to **Google Cloud Run** with Terraform, receiving the API URL as an environment variable set by the infrastructure code.
