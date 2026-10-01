/**
 * Tests for DELETE /tasks/:id
 *
 * These tests mock the db module so no real PostgreSQL connection is needed.
 * They import the Express app directly after replacing db.js with a stub.
 */
const { test } = require('node:test');
const assert = require('node:assert/strict');
const http = require('node:http');

// ---------------------------------------------------------------------------
// Helper: create a temporary HTTP server around the app and make one request
// ---------------------------------------------------------------------------
function withServer(app, fn) {
    return new Promise((resolve, reject) => {
        const server = http.createServer(app);
        server.listen(0, '127.0.0.1', async () => {
            const { port } = server.address();
            try {
                const result = await fn(port);
                server.close();
                resolve(result);
            } catch (err) {
                server.close();
                reject(err);
            }
        });
    });
}

// ---------------------------------------------------------------------------
// Load a fresh copy of index.js with an injected db stub
// ---------------------------------------------------------------------------
function loadApp(queryFn) {
    const apiPath = require.resolve('../index.js');
    const dbPath  = require.resolve('../db.js');
    delete require.cache[apiPath];
    delete require.cache[dbPath];

    // Inject stub
    require.cache[dbPath] = {
        id: dbPath,
        filename: dbPath,
        loaded: true,
        exports: { query: queryFn },
    };

    return require('../index.js');
}

// ---------------------------------------------------------------------------
// DELETE /tasks/:id — 204 when row exists
// ---------------------------------------------------------------------------
test('DELETE /tasks/:id returns 204 for an existing task', async () => {
    const app = loadApp(async () => ({ rowCount: 1, rows: [] }));

    const res = await withServer(app, (port) =>
        fetch(`http://127.0.0.1:${port}/tasks/42`, { method: 'DELETE' })
    );

    assert.equal(res.status, 204);
    const body = await res.text();
    assert.equal(body, '');
});

// ---------------------------------------------------------------------------
// DELETE /tasks/:id — 404 when row does not exist
// ---------------------------------------------------------------------------
test('DELETE /tasks/:id returns 404 for a missing task', async () => {
    const app = loadApp(async () => ({ rowCount: 0, rows: [] }));

    const res = await withServer(app, (port) =>
        fetch(`http://127.0.0.1:${port}/tasks/999`, { method: 'DELETE' })
    );

    assert.equal(res.status, 404);
    const json = await res.json();
    assert.equal(json.error, 'Not found');
});
