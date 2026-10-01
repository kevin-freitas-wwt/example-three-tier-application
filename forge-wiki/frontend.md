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
│   ├── layout.tsx      # Root layout with dark mode support
│   ├── page.tsx        # Home page with task list UI
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

Exports three async functions that fetch from the backend API:

```typescript
getTasks(): Promise<Task[]>        // Fetch all tasks
createTask(formData: FormData)      // Create a new task
toggleTask(id: number, completed: boolean)  // Update task completion status
```

#### `app/page.tsx`

The main page component:
- Fetches all tasks server-side using `getTasks()`
- Renders a form to add new tasks (calls `createTask` on submit)
- Displays task list with checkbox to toggle completion
- Shows progress counter (completed / total)
- Supports dark mode with Tailwind CSS

### Styling

- **Tailwind CSS 4** for styling
- **Dark mode support** via `dark:` class variants
- **Responsive design** with mobile-first approach
- **Accessible UI** with semantic HTML and ARIA labels

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

// PATCH /tasks/:id
await fetch(`${API_URL}/tasks/${id}`, {
  method: 'PATCH',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ completed })
});
```

After each mutation, `revalidatePath('/')` refreshes the page data.

## Deployment

The frontend is deployed to **Google Cloud Run** with Terraform, receiving the API URL as an environment variable set by the infrastructure code.
