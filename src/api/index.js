const express = require('express');
const db = require('./db');

const app = express();
const PORT = process.env.PORT || 3001;

app.use(express.json());

app.get('/health', (_req, res) => {
  res.json({ status: 'ok' });
});

// GET /tasks — list all tasks
app.get('/tasks', async (_req, res) => {
  const { rows } = await db.query('SELECT * FROM tasks ORDER BY created_at ASC');
  res.json(rows);
});

// POST /tasks — create a task
app.post('/tasks', async (req, res) => {
  const { title } = req.body;
  if (!title || typeof title !== 'string' || !title.trim()) {
    return res.status(400).json({ error: 'title is required' });
  }
  const { rows } = await db.query(
    'INSERT INTO tasks (title) VALUES ($1) RETURNING *',
    [title.trim()]
  );
  res.status(201).json(rows[0]);
});

// PATCH /tasks/:id — update a task (complete/uncomplete or rename)
app.patch('/tasks/:id', async (req, res) => {
  const id = parseInt(req.params.id, 10);
  const { completed, title } = req.body;

  const { rows } = await db.query('SELECT * FROM tasks WHERE id = $1', [id]);
  if (rows.length === 0) return res.status(404).json({ error: 'Not found' });

  const current = rows[0];
  const newCompleted = completed !== undefined ? Boolean(completed) : current.completed;
  const newTitle = title !== undefined ? title.trim() : current.title;

  const { rows: updated } = await db.query(
    'UPDATE tasks SET completed = $1, title = $2 WHERE id = $3 RETURNING *',
    [newCompleted, newTitle, id]
  );
  res.json(updated[0]);
});

// GET /food-entries — list all food entries, newest first
app.get('/food-entries', async (_req, res) => {
  const { rows } = await db.query('SELECT * FROM food_entries ORDER BY logged_at DESC');
  res.json(rows);
});

// POST /food-entries — create a food entry
app.post('/food-entries', async (req, res) => {
  const { name, calories } = req.body;
  if (!name || typeof name !== 'string' || !name.trim()) {
    return res.status(400).json({ error: 'name is required' });
  }
  const caloriesNum = Number(calories);
  if (!Number.isFinite(caloriesNum) || !Number.isInteger(caloriesNum) || caloriesNum <= 0) {
    return res.status(400).json({ error: 'calories must be a positive integer' });
  }
  const { rows } = await db.query(
    'INSERT INTO food_entries (name, calories) VALUES ($1, $2) RETURNING *',
    [name.trim(), caloriesNum]
  );
  res.status(201).json(rows[0]);
});

// DELETE /food-entries/:id — remove a food entry
app.delete('/food-entries/:id', async (req, res) => {
  const id = parseInt(req.params.id, 10);
  const { rows } = await db.query('DELETE FROM food_entries WHERE id = $1 RETURNING *', [id]);
  if (rows.length === 0) return res.status(404).json({ error: 'Not found' });
  res.status(204).end();
});

app.listen(PORT, () => {
  console.log(`API listening on port ${PORT}`);
});
