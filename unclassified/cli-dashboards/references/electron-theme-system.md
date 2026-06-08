## CSS Theme System with Custom Properties

All colors, fonts, and effects live in CSS custom properties. Themes switch by setting a `data-theme` attribute on `<html>`.

### themes.css structure

```css
/* Base structure (never changes) */
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
  width: 100%; height: 100%;
  font-family: var(--font-body);
  background: var(--bg);
  color: var(--text-bright);
}

/* Theme: Phosphor (default) */
[data-theme="phosphor"], :root {
  --bg: #070a07;
  --bg-panel: #0d120d;
  --border-red: #c43e3e;
  --border-cyan: #2a9d8f;
  --text-dim: #2d4a2d;
  --text-med: #5a8a5a;
  --text-bright: #8fbc8f;
  --red: #ff4d4d;
  --red-dim: #8b2222;
  --cyan: #00e5ff;
  --cyan-dim: #006b7a;
  --amber: #ffb000;
  --amber-dim: #8a6000;
  --grid: #112211;
  --crt-scan: rgba(0,0,0,0.18);
  --crt-vignette: rgba(0,20,0,0.5);
  --font-body: 'Courier New', Courier, monospace;
  --font-header: 'Courier New', Courier, monospace;
  --panel-radius: 0px;
  --border-width: 1px;
  --glow-intensity: 1.0;
}

/* Add more themes the same way */
[data-theme="cyberpunk"] { ... }
[data-theme="military"] { ... }
```

### Switching themes in JS

```javascript
const THEME_KEY = 'my-app-theme';
const DEFAULT_THEME = 'phosphor';

function applyTheme(name) {
  document.documentElement.setAttribute('data-theme', name);
  try { localStorage.setItem(THEME_KEY, name); } catch (e) {}
}

function initTheme() {
  let saved;
  try { saved = localStorage.getItem(THEME_KEY); } catch (e) {}
  applyTheme(saved || DEFAULT_THEME);
}
initTheme();
```

### Theme builder bridge

The builder sends updates via `postMessage`. The dashboard listens:

```javascript
window.addEventListener('message', (e) => {
  if (e.data?.type === 'theme') {
    const t = e.data.data;
    // Apply each variable directly
    document.documentElement.style.setProperty('--bg', t.bg);
    document.documentElement.style.setProperty('--cyan', t.cyan);
    // ... all variables
    document.body.style.fontFamily = t.font;
  }
});
```

This allows live preview without reloading the iframe.
