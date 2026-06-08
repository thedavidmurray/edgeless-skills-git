const { app, BrowserWindow, Tray, Menu, nativeImage, ipcMain } = require('electron');
const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');
const { URL } = require('url');

const JAEGER = process.env.OTEL_DASHBOARD_JAEGER || 'http://localhost:16687';
const APP_PORT = 8766;

let mainWindow;
let tray;
let server;

function startProxyServer() {
  server = http.createServer((req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    if (req.method === 'OPTIONS') { res.writeHead(200); res.end(); return; }

    if (req.url === '/' || req.url === '/index.html') {
      const htmlPath = path.join(__dirname, 'index.html');
      fs.readFile(htmlPath, (err, data) => {
        if (err) { res.writeHead(500); res.end('Error loading dashboard'); return; }
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.end(data);
      });
      return;
    }

    if (req.url.startsWith('/jaeger/')) {
      const targetPath = req.url.slice('/jaeger'.length);
      const targetUrl = new URL(targetPath + (req.url.includes('?') ? '' : ''), JAEGER);
      if (req.url.includes('?')) targetUrl.search = req.url.split('?')[1];

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
    console.log(`[Proxy] Dashboard: http://127.0.0.1:${APP_PORT}`);
    console.log(`[Proxy] Jaeger:    ${JAEGER}`);
  });

  server.on('error', (err) => {
    if (err.code === 'EADDRINUSE') {
      console.log(`[Proxy] Port ${APP_PORT} already in use`);
    } else {
      console.error('[Proxy] Server error:', err);
    }
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400, height: 900, minWidth: 1000, minHeight: 600,
    title: 'Dashboard', backgroundColor: '#070a07', show: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true, nodeIntegration: false, webSecurity: false,
    },
    titleBarStyle: 'hiddenInset',
    trafficLightPosition: { x: 12, y: 10 },
  });
  mainWindow.loadURL(`http://127.0.0.1:${APP_PORT}`);
  mainWindow.once('ready-to-show', () => mainWindow.show());
  mainWindow.on('closed', () => { mainWindow = null; });
}

function createTray() {
  const iconPath = path.join(__dirname, 'assets', 'icon.png');
  let icon = fs.existsSync(iconPath) ? nativeImage.createFromPath(iconPath) : nativeImage.createEmpty();
  tray = new Tray(icon);
  const contextMenu = Menu.buildFromTemplate([
    { label: 'Show Dashboard', click: () => {
      if (mainWindow) { mainWindow.show(); mainWindow.focus(); }
      else { createWindow(); }
    }},
    { type: 'separator' },
    { label: 'Open Jaeger UI', click: () => { require('electron').shell.openExternal(JAEGER); }},
    { type: 'separator' },
    { label: 'Quit', click: () => { app.quit(); } },
  ]);
  tray.setToolTip('OTEL Dashboard');
  tray.setContextMenu(contextMenu);
  tray.on('click', () => {
    if (mainWindow) { mainWindow.isVisible() ? mainWindow.hide() : mainWindow.show(); }
    else { createWindow(); }
  });
}

app.whenReady().then(() => {
  startProxyServer();
  createWindow();
  createTray();
  app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
});
app.on('window-all-closed', () => {});
app.on('quit', () => { if (server) server.close(); });

ipcMain.handle('get-app-version', () => app.getVersion());
ipcMain.handle('get-jaeger-status', async () => {
  return new Promise((resolve) => {
    const req = http.get(`${JAEGER}/api/services`, { timeout: 3000 }, (res) => {
      resolve({ online: res.statusCode === 200 });
    });
    req.on('error', () => resolve({ online: false }));
    req.on('timeout', () => { req.destroy(); resolve({ online: false }); });
  });
});
