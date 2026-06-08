## Embedded Node.js Proxy Server

The proxy serves static files and forwards API requests to the backend. No separate server process needed.

```javascript
const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');
const { URL } = require('url');

const APP_PORT = 8766;
const BACKEND = 'http://localhost:16687'; // Jaeger, Prometheus, etc.

const server = http.createServer((req, res) => {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') { res.writeHead(200); res.end(); return; }

  // Static files
  const staticRoutes = {
    '/': { file: 'index.html', mime: 'text/html' },
    '/index.html': { file: 'index.html', mime: 'text/html' },
    '/themes.css': { file: 'themes.css', mime: 'text/css' },
    '/theme-builder.html': { file: 'theme-builder.html', mime: 'text/html' },
  };

  if (staticRoutes[req.url]) {
    const { file, mime } = staticRoutes[req.url];
    fs.readFile(path.join(__dirname, file), (err, data) => {
      if (err) { res.writeHead(500); res.end(`Error loading ${file}`); return; }
      res.writeHead(200, { 'Content-Type': mime });
      res.end(data);
    });
    return;
  }

  // Proxy /api/* to backend
  if (req.url.startsWith('/api/')) {
    const targetUrl = new URL(req.url, BACKEND);
    const client = targetUrl.protocol === 'https:' ? https : http;
    const proxyReq = client.request(targetUrl, {
      method: req.method,
      headers: { ...req.headers, host: targetUrl.host },
    }, (proxyRes) => {
      res.writeHead(proxyRes.statusCode, proxyRes.headers);
      proxyRes.pipe(res);
    });
    proxyReq.on('error', (err) => {
      res.writeHead(502, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: err.message }));
    });
    req.pipe(proxyReq);
    return;
  }

  res.writeHead(404); res.end('Not found');
});

server.listen(APP_PORT, '127.0.0.1', () => {
  console.log(`[Proxy] http://127.0.0.1:${APP_PORT}`);
});
```

Key points:
- Serve `index.html`, `themes.css`, `theme-builder.html` from `__dirname`
- Proxy `/api/*` to the backend (Jaeger, Prometheus, custom API)
- Add CORS headers so the browser doesn't block anything
- Handle errors gracefully (502 for backend down)
