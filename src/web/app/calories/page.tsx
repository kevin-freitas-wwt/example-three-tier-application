import Link from 'next/link';
import { getFoodEntries, createFoodEntry, deleteFoodEntry } from './actions';

export default async function CaloriesPage() {
  const entries = await getFoodEntries();
  const total = entries.reduce((sum, entry) => sum + entry.calories, 0);

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-900 py-16 px-4">
      <div className="max-w-lg mx-auto">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold text-zinc-900 dark:text-zinc-50">
            Calorie Tracker
          </h1>
          <Link
            href="/"
            className="text-sm font-medium text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-50 transition-colors"
          >
            ← To-Do List
          </Link>
        </div>

        {/* Add food entry form */}
        <form action={createFoodEntry} className="flex gap-2 mb-8">
          <input
            name="name"
            type="text"
            required
            placeholder="Food name..."
            className="flex-1 rounded-lg border border-zinc-300 dark:border-zinc-600 bg-white dark:bg-zinc-800 px-4 py-2 text-zinc-900 dark:text-zinc-50 placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-zinc-500"
          />
          <input
            name="calories"
            type="number"
            required
            min="1"
            step="1"
            placeholder="Calories"
            className="w-28 rounded-lg border border-zinc-300 dark:border-zinc-600 bg-white dark:bg-zinc-800 px-4 py-2 text-zinc-900 dark:text-zinc-50 placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-zinc-500"
          />
          <button
            type="submit"
            className="rounded-lg bg-zinc-900 dark:bg-zinc-50 px-5 py-2 font-medium text-white dark:text-zinc-900 hover:bg-zinc-700 dark:hover:bg-zinc-200 transition-colors"
          >
            Add
          </button>
        </form>

        {/* Food entry list */}
        <ul className="space-y-2">
          {entries.length === 0 && (
            <li className="text-zinc-400 text-center py-8">No food logged yet. Add one above!</li>
          )}
          {entries.map((entry) => (
            <li
              key={entry.id}
              className="flex items-center gap-3 rounded-lg border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 px-4 py-3"
            >
              <span className="flex-1 text-sm text-zinc-800 dark:text-zinc-100">
                {entry.name}
              </span>
              <span className="text-sm text-zinc-500 dark:text-zinc-400">
                {entry.calories} cal
              </span>
              <form
                action={async () => {
                  'use server';
                  await deleteFoodEntry(entry.id);
                }}
              >
                <button
                  type="submit"
                  aria-label="Delete entry"
                  className="text-zinc-400 hover:text-red-500 transition-colors"
                >
                  ✕
                </button>
              </form>
            </li>
          ))}
        </ul>

        {entries.length > 0 && (
          <p className="mt-4 text-sm font-medium text-zinc-700 dark:text-zinc-200 text-right">
            Total: {total} cal
          </p>
        )}
      </div>
    </div>
  );
}
