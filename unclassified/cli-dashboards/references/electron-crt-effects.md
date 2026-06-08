## CRT Effects (Scanlines, Vignette, Glow, Flicker)

Pure CSS. No canvas, no JS. `pointer-events: none` so they don't block clicks.

### Scanlines

```css
body::before {
  content: '';
  position: fixed; inset: 0;
  background: repeating-linear-gradient(
    0deg,
    var(--crt-scan) 0px,
    var(--crt-scan) 1px,
    transparent 1px,
    transparent 2px
  );
  pointer-events: none;
  z-index: 9999;
  mix-blend-mode: multiply;
}
```

Adjust `--crt-scan` opacity per theme (0.03 for Matrix, 0.22 for Cyberpunk).

### Vignette

```css
body::after {
  content: '';
  position: fixed; inset: 0;
  background: radial-gradient(
    ellipse at center,
    transparent 55%,
    var(--crt-vignette) 100%
  );
  pointer-events: none;
  z-index: 9998;
}
```

### Glow Text (scaled by intensity)

```css
.glow-red {
  text-shadow:
    0 0 calc(4px * var(--glow-intensity)) var(--red-dim),
    0 0 calc(10px * var(--glow-intensity)) var(--red);
}
.glow-cyan {
  text-shadow:
    0 0 calc(4px * var(--glow-intensity)) var(--cyan-dim),
    0 0 calc(10px * var(--glow-intensity)) var(--cyan);
}
```

`--glow-intensity` is a multiplier (0 = no glow, 1 = default, 3 = heavy).

### Flicker Animation

```css
@keyframes flicker {
  0%, 100% { opacity: 1; }
  50% { opacity: .98; }
  52% { opacity: .85; }
  54% { opacity: .98; }
  90% { opacity: .97; }
}
.flicker { animation: flicker 4s infinite; }
```

### Breathing Pulse

```css
@keyframes breathe {
  0%, 100% { opacity: .6; }
  50% { opacity: 1; }
}
.breathe { animation: breathe 2s ease-in-out infinite; }
```

Apply to status dots, alert borders, or live indicators.
