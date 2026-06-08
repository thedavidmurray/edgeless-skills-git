const { contextBridge, ipcRenderer } = require('electron');

// Safe IPC bridge between renderer (dashboard HTML) and main process.
// Exposes only explicitly-approved channels to the browser context.
// Used by the embedded proxy dashboard in the EDGELESS OTEL Command app.

contextBridge.exposeInMainWorld('electronAPI', {
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  getJaegerStatus: () => ipcRenderer.invoke('get-jaeger-status'),
});
