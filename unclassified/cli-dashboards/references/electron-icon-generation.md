## App Icon Generation with Python PIL

When no designer asset is available, generate a 512x512 icon programmatically.

```python
from PIL import Image, ImageDraw

size = 512
bg_color = (7, 10, 7, 255)
border_color = (42, 157, 143, 255)  # --border-cyan
accent = (0, 229, 255, 255)  # --cyan

img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Rounded rect background
corner = 80
draw.rounded_rectangle(
    [10, 10, size-10, size-10],
    radius=corner,
    fill=bg_color,
    outline=border_color,
    width=8
)

# Grid pattern
for i in range(0, size, 40):
    draw.line([(i, 80), (i, size-80)], fill=(17, 34, 17, 120), width=1)
    draw.line([(80, i), (size-80, i)], fill=(17, 34, 17, 120), width=1)

# Center glow circle (the 'O' in OTEL)
cx, cy = size//2, size//2
draw.ellipse([cx-100, cy-100, cx+100, cy+100], outline=accent, width=12)
draw.ellipse([cx-20, cy-20, cx+20, cy+20], fill=accent)

# Bars on sides (signal visualization)
bar_w = 20
gap = 12
for side in [-1, 1]:
    for i in range(6):
        h = 60 + i * 30
        x = cx + side * (140 + i * (bar_w + gap))
        if side == -1:
            draw.rectangle([x, cy-h//2, x+bar_w, cy+h//2], fill=(accent[0], accent[1], accent[2], 180))
        else:
            draw.rectangle([x-bar_w, cy-h//2, x, cy+h//2], fill=(accent[0], accent[1], accent[2], 180))

img.save('assets/icon.png')
```

Also generate smaller sizes for macOS iconsets:

```python
import shutil
for sz in [256, 128, 64, 32, 16]:
    img.resize((sz, sz), Image.LANCZOS).save(f'assets/icon_{sz}x{sz}.png')
```

On macOS, bundle into `.icns`:

```bash
mkdir -p EdgelessIcon.iconset
cp icon_16x16.png EdgelessIcon.iconset/icon_16x16.png
cp icon_32x32.png EdgelessIcon.iconset/icon_16x16@2x.png
# ... more sizes ...
iconutil -c icns EdgelessIcon.iconset
rm -rf EdgelessIcon.iconset
```
