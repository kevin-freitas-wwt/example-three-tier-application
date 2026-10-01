'use client';

import { useOptimistic, useState, useTransition, useRef } from 'react';
import { createTask, toggleTask, deleteTask, updateTaskTitle } from './actions';
import type { Task } from './actions';

type Filter = 'all' | 'active' | 'completed';

interface TaskRowProps {
  task: Task & { pending?: boolean };
  onToggle: (id: number, completed: boolean) => void;
  onDelete: (id: number) => void;
  onRename: (id: number, newTitle: string, originalTitle: string) => void;
}

function TaskRow({ task, onToggle, onDelete, onRename }: TaskRowProps) {
  const [editing, setEditing] = useState(false);
  const [editValue, setEditValue] = useState(task.title);
  const inputRef = useRef<HTMLInputElement>(null);

  function commitEdit() {
    const trimmed = editValue.trim();
    if (trimmed && trimmed !== task.title) {
      onRename(task.id, trimmed, task.title);
    }
    setEditing(false);
  }

  function startEdit() {
    if (task.completed || task.pending) return;
    setEditValue(task.title);
    setEditing(true);
    // Focus is handled by autoFocus on the input
  }

  function cancelEdit() {
    setEditValue(task.title);
    setEditing(false);
  }

  return (
    <li
      className={`flex items-center gap-3 rounded-lg border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 px-4 py-3 transition-opacity ${
        task.pending ? 'opacity-50' : 'opacity-100'
      }`}
    >
      {/* Checkbox button */}
      <button
        type="button"
        onClick={() => !task.pending && onToggle(task.id, !task.completed)}
        className={`h-5 w-5 rounded border-2 flex-shrink-0 transition-colors focus-visible:ring-2 focus-visible:ring-zinc-500 focus-visible:ring-offset-2 ${
          task.completed
            ? 'bg-zinc-900 dark:bg-zinc-50 border-zinc-900 dark:border-zinc-50'
            : 'border-zinc-300 dark:border-zinc-600 hover:border-zinc-500'
        }`}
        aria-label={task.completed ? 'Mark incomplete' : 'Mark complete'}
        disabled={task.pending}
      >
        {task.completed && (
          <svg
            viewBox="0 0 12 12"
            className="text-white dark:text-zinc-900 w-full h-full p-0.5"
          >
            <path
              d="M2 6l3 3 5-5"
              stroke="currentColor"
              strokeWidth="1.5"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        )}
      </button>

      {/* Title — editable or static */}
      <span className="flex-1 text-sm min-w-0">
        {editing ? (
          <input
            ref={inputRef}
            autoFocus
            type="text"
            value={editValue}
            onChange={(e) => setEditValue(e.target.value)}
            onBlur={commitEdit}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                commitEdit();
              } else if (e.key === 'Escape') {
                cancelEdit();
              }
            }}
            className="w-full rounded border border-zinc-300 dark:border-zinc-600 bg-zinc-50 dark:bg-zinc-700 px-2 py-0.5 text-zinc-900 dark:text-zinc-50 focus:outline-none focus:ring-2 focus:ring-zinc-500"
            aria-label="Edit task title"
          />
        ) : (
          <span
            onClick={startEdit}
            title={task.completed ? undefined : 'Click to edit'}
            className={`block truncate ${
              task.completed
                ? 'line-through text-zinc-400 cursor-default'
                : 'text-zinc-800 dark:text-zinc-100 cursor-text'
            }`}
          >
            {task.title}
          </span>
        )}
      </span>

      {/* Delete button */}
      <button
        type="button"
        onClick={() => !task.pending && onDelete(task.id)}
        aria-label="Delete task"
        disabled={task.pending}
        className="flex-shrink-0 text-zinc-300 dark:text-zinc-600 hover:text-red-500 dark:hover:text-red-400 transition-colors text-lg leading-none focus-visible:ring-2 focus-visible:ring-zinc-500 focus-visible:ring-offset-2 rounded"
      >
        ×
      </button>
    </li>
  );
}

export default function TaskList({ initialTasks }: { initialTasks: Task[] }) {
  const [filter, setFilter] = useState<Filter>('all');
  const [inputValue, setInputValue] = useState('');
  const [, startTransition] = useTransition();

  type OptimisticTask = Task & { pending?: boolean };

  const [optimisticTasks, addOptimisticTask] = useOptimistic<
    OptimisticTask[],
    OptimisticTask
  >(initialTasks, (state, newTask) => [...state, newTask]);

  const visibleTasks = optimisticTasks.filter((t) => {
    if (filter === 'active') return !t.completed;
    if (filter === 'completed') return t.completed;
    return true;
  });

  async function handleAdd(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const title = inputValue.trim();
    if (!title) return;

    const formData = new FormData();
    formData.set('title', title);

    setInputValue('');

    startTransition(async () => {
      addOptimisticTask({
        id: -Date.now(),
        title,
        completed: false,
        created_at: '',
        pending: true,
      });
      await createTask(formData);
    });
  }

  function handleToggle(id: number, completed: boolean) {
    startTransition(async () => {
      await toggleTask(id, completed);
    });
  }

  function handleDelete(id: number) {
    startTransition(async () => {
      await deleteTask(id);
    });
  }

  function handleRename(id: number, newTitle: string, originalTitle: string) {
    startTransition(async () => {
      await updateTaskTitle(id, newTitle, originalTitle);
    });
  }

  const filterBtnClass = (f: Filter) =>
    `px-3 py-1 rounded-full text-xs font-medium transition-colors focus-visible:ring-2 focus-visible:ring-zinc-500 focus-visible:ring-offset-2 ${
      filter === f
        ? 'bg-zinc-900 dark:bg-zinc-50 text-white dark:text-zinc-900'
        : 'border border-zinc-300 dark:border-zinc-600 text-zinc-600 dark:text-zinc-400 hover:border-zinc-500 dark:hover:border-zinc-400'
    }`;

  const completedCount = optimisticTasks.filter((t) => t.completed && !t.pending).length;
  const totalCount = optimisticTasks.filter((t) => !t.pending).length;

  return (
    <>
      {/* Add task form */}
      <form onSubmit={handleAdd} className="flex gap-2 mb-6">
        <input
          name="title"
          type="text"
          required
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Add a new task..."
          className="flex-1 rounded-lg border border-zinc-300 dark:border-zinc-600 bg-white dark:bg-zinc-800 px-4 py-2 text-zinc-900 dark:text-zinc-50 placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-zinc-500"
        />
        <button
          type="submit"
          className="rounded-lg bg-zinc-900 dark:bg-zinc-50 px-5 py-2 font-medium text-white dark:text-zinc-900 hover:bg-zinc-700 dark:hover:bg-zinc-200 transition-colors"
        >
          Add
        </button>
      </form>

      {/* Filter tabs — only shown when there are tasks */}
      {optimisticTasks.length > 0 && (
        <div className="flex gap-2 mb-4">
          <button className={filterBtnClass('all')} onClick={() => setFilter('all')}>
            All
          </button>
          <button className={filterBtnClass('active')} onClick={() => setFilter('active')}>
            Active
          </button>
          <button
            className={filterBtnClass('completed')}
            onClick={() => setFilter('completed')}
          >
            Completed
          </button>
        </div>
      )}

      {/* Task list */}
      <ul className="space-y-2">
        {visibleTasks.length === 0 ? (
          <li className="flex flex-col items-center gap-3 py-12 text-zinc-400 select-none">
            <span className="text-5xl" aria-hidden="true">
              📋
            </span>
            <span className="text-sm">No tasks yet. Add one above!</span>
          </li>
        ) : (
          visibleTasks.map((task) => (
            <TaskRow
              key={task.id}
              task={task}
              onToggle={handleToggle}
              onDelete={handleDelete}
              onRename={handleRename}
            />
          ))
        )}
      </ul>

      {/* Progress count */}
      {totalCount > 0 && (
        <p className="mt-4 text-xs text-zinc-400 text-right">
          {completedCount} / {totalCount} completed
        </p>
      )}
    </>
  );
}
