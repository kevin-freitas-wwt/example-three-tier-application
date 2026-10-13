const { test } = require('node:test');
const assert = require('node:assert/strict');
const { spawn } = require('node:child_process');
const net = require('node:net');
const path = require('node:path');
const { version } = require('../package.json');

function freePort() {
    return new Promise((resolve, reject) => {
        const srv = net.createServer();
        srv.unref();
        srv.on('error', reject);
        srv.listen(0, () => {
            const { port } = srv.address();
            srv.close(() => resolve(port));
        });
    });
}

async function waitForHealth(url, child, timeoutMs) {
    const deadline = Date.now() + timeoutMs;
    while (Date.now() < deadline) {
        if (child.exitCode !== null) {
            throw new Error(`API exited early with code ${child.exitCode}`);
        }
        try {
            return await fetch(url);
        } catch {
            await new Promise((r) => setTimeout(r, 100));
        }
    }
    throw new Error(`API did not respond at ${url} within ${timeoutMs}ms`);
}

test('GET /api/version returns the package version', async (t) => {
    const port = await freePort();
    const child = spawn(process.execPath, [path.join(__dirname, '..', 'index.js')], {
        env: { ...process.env, PORT: String(port), DATABASE_URL: '[redacted: credential]' },
        stdio: ['ignore', 'ignore', 'inherit'],
    });
    t.after(() => child.kill());

    await waitForHealth(`http://127.0.0.1:${port}/health`, child, 5000);

    const res = await fetch(`http://127.0.0.1:${port}/api/version`);
    assert.equal(res.status, 200);
    assert.deepEqual(await res.json(), { version });
});
