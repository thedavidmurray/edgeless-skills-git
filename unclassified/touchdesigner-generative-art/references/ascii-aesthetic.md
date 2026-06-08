# ASCII Aesthetic in TouchDesigner — Techniques

Terminal/CLI visual language for branded generative art.

## Typography System

### Monospace Fonts
```
Primary: Courier (system, always available)
Fallback: Monaco, Consolas, Lucida Console
Use for: All identity, timestamps, agent IDs, status text
Avoid for: Decorative/flourish text (breaks terminal aesthetic)
```

### Text Formatting Patterns

**Agent Identity:**
```
Format: YYYY-MM-DD :: AgentName#ID
Example: 2026-04-29 :: Hive#2662
         2026-04-29 :: Kilo#3551
         2026-04-29 :: Beau (VPS)
```

**Swarm Notation:**
```
BRAND ██████ PROJECT ▓▓▓▓▓▓ COMPONENT
[AGENT] ===== [TYPE:EXECUTE] ===== [REF:EDGA-001]
```

**Status Lines:**
```
STATUS: ACTIVE  FPS: 60.0  FRAME: 015947  [SWARM SYNC]
```

## Grid Density Allusions

### Character Cell Mapping
Use SOP/TOP dimensions that evoke terminal resolutions:

| Grid Size | Terminal Equivalent | Visual Effect |
|-----------|---------------------|---------------|
| 80×25 | Standard terminal | Classic CLI window |
| 32×32 | 1024 characters | "High density" ASCII art |
| 40×25 | 1000 characters | Retro computing feel |
| 64×64 | 4096 characters | Dense terminal matrix |

### Implementation (gridSOP)
```python
# 32×32 for swarm/grid visualization
grid_sop.par.rows = 32
grid_sop.par.cols = 32
grid_sop.par.size = (10, 10)

# Visible wireframe = ASCII cell boundaries
grid_sop.par.wireframe = True
```

### Implementation (CHOP→TOP texture)
```python
# 80×1 texture = single terminal line
chop_to_top.par.resolutionw = 80
chop_to_top.par.resolutionh = 1
chop_to_top.par.dataformat = 'r'  # Red channel = intensity
```

## Unicode Block Characters

### Character Set
```
█ U+2588  FULL BLOCK         (100% fill)
▉ U+2589  LEFT SEVEN EIGHTHS (87.5%)
▊ U+258A  LEFT THREE FOURTHS (75%)
▋ U+258B  LEFT FIVE EIGHTHS  (62.5%)
▌ U+258C  LEFT HALF          (50%)
▍ U+258D  LEFT THREE EIGHTHS (37.5%)
▎ U+258E  LEFT ONE FOURTH    (25%)
▏ U+258F  LEFT ONE EIGHTH    (12.5%)

▓ U+2593  DARK SHADE
▒ U+2592  MEDIUM SHADE  
░ U+2591  LIGHT SHADE

▀ U+2580  UPPER HALF BLOCK
▄ U+2584  LOWER HALF BLOCK
```

### Usage Patterns

**Separators:**
```
AGENT ██████ HIVE ██████ COORDINATING
"██████" = 6-char block separator (72px wide at 12pt)
```

**Progress Bars:**
```
[████████░░░░░░░░░░] 45%
# 10 total blocks, 4.5 filled → ▉ for half blocks
```

**Intensity Mapping:**
```python
# Map 0-1 value to block character
def value_to_block(v):
    if v > 0.875: return '█'
    if v > 0.75:  return '▉'
    if v > 0.625: return '▊'
    if v > 0.5:   return '▋'
    if v > 0.375: return '▌'
    if v > 0.25:  return '▍'
    if v > 0.125: return '▎'
    return '▏'
```

## Color Palette — Terminal Standard

### Standard 16-Color Terminal
```
Black:   #000000   (Background)
Red:     #FF6B6B   (Errors, alerts)
Green:   #00FF88   (Success, positive)
Yellow:  #FFD93D   (Warnings)
Blue:    #6BCB77   (Links, info)
Magenta: #9D4EDD   (Secondary)
Cyan:    #00D4FF   (Primary, brand)
White:   #F0F0F0   (Text)

Bright variants: Same hue, +20% luminance
```

### Edgeless Brand Mapping
```
Cyan    #00D4FF → Primary terminal color (headers, identity)
Purple  #9D4EDD → Magenta (swarm agents, secondary)
Green   #00FF88 → Success/confirmation, active state
Black   #0A0A0A → Background (not pure black for softer glow)
White   #F0F0F0 → Body text (slightly warm)
```

## Motion Patterns

### Cursor Blink Evocation
```python
# Subtle opacity pulse = active cursor
text_op.par.opacity.expr = '0.8 + 0.2 * (absTime.frame % 30 < 15)'
# 15 frames on, 15 frames off at 30fps = ~1Hz blink
```

### Typing Effect
```python
# Reveal characters one by one
full_text = "SYSTEM INITIALIZED"
text_op.par.text.expr = f'"{full_text}"[:int(absTime.seconds * 10) % {len(full_text)+1}]'
# 10 chars per second typing speed
```

### Scroll/Terminal Output
```python
# CHOP shift for scrolling text lines
shift_chop = base.create(shiftCHOP, 'line_scroll')
shift_chop.par.shift = -1  # Move up one line per frame
shift_chop.par.timeslice = True
```

### Loading/Spinner
```python
spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']  # Braille spinner
spinner_text.par.text.expr = f'"PROCESSING {spinner_chars[int(absTime.frame / 3) % 10]}"'
# 3 frames per char at 30fps = 10Hz spin
```

## CRT/Retro Terminal Effects

### Scan Lines (via GLSL or noise)
```glsl
// Every other line darker
float scanline = mod(gl_FragCoord.y, 2.0) < 1.0 ? 0.9 : 1.0;
fragColor *= scanline;
```

### Screen Glow/Bloom
```python
# Blur TOP with 1-2px radius
glow = base.create(blurTOP, 'crt_glow')
glow.par.size = 1
glow.par.type = 'gaussian'
glow.par.alpha = 0.3  # Subtle glow only
```

### Curvature (vertex displacement)
```python
# Slight barrel distortion on corners
# Use displaceTOP with radial gradient
```

### Phosphor Decay (feedback)
```python
# Feedback TOP for trail/ghost effect
feedback = base.create(feedbackTOP, 'phosphor')
feedback.par.feedback = 0.8  # 80% previous frame retained
```

## Integration Examples

### Full Status HUD
```
┌────────────────────────────────────────────────────────────┐
│  2026-04-29 :: Hive#2662        [████████░░░] 78%          │
│  SWARM: 5 agents active                                       │
│  ├─ Kilo   [EXECUTE]  ████████████████████ DONE            │
│  ├─ Beau   [VPS]      ██████████████░░░░░░ 60%            │
│  ├─ Scribe [ENRICH]   ░░░░░░░░░░░░░░░░░░░░ IDLE            │
│  └─ Hive   [COORD]    ████████████████████ ACTIVE          │
└────────────────────────────────────────────────────────────┘
```

### TextTOP Layout
```python
# Main identity (large, cyan)
id_text.par.fontsize = 24
id_text.par.color = (0.0, 0.831, 1.0)  # Cyan
id_text.par.text = "EDGELESS ██████ HERMES ██████ SWARM"

# Timestamp (small, purple, corner)
ts_text.par.fontsize = 14
ts_text.par.color = (0.616, 0.302, 0.867)  # Purple
ts_text.par.text = "2026-04-29 :: Hive#2662"
ts_text.par.alignx = 'left'
ts_text.par.translatex = 20
ts_text.par.translatey = 680  # Bottom-left
```

## Font Availability Matrix

| Font | macOS | Windows | Linux | Use Case |
|------|-------|---------|-------|----------|
| Courier | ✅ | ✅ | ✅ | Primary, guaranteed |
| Monaco | ✅ | ❌ | ❌ | macOS native look |
| Consolas | ❌ | ✅ | ❌ | Windows native look |
| Lucida Console | ✅ | ✅ | ❌ | Fallback |
| Menlo | ✅ | ❌ | ❌ | Terminal.app style |

## Implementation Notes

### Text Rendering Performance
- Cache static text to nullTOP
- Only animate dynamic elements
- Use `resolutionw/h` to match output (crisp pixels)
- `pixel format = 8-bit fixed` for retro look

### Monospace Alignment
- All characters same width = easy column alignment
- Use spaces for padding: `"[AGENT]   [STATUS]"`
- Fixed-width numbers: `f"{count:4d}"` = `"  42"`

### Combining with 3D
- Text as texture on cards/POPs
- 3D swarm behind 2D text overlay
- Depth separation: Text at Z=0, particles at Z=-5 to +5

## References

- Unicode Block Elements: https://unicode.org/charts/PDF/U2580.pdf
- Braille Patterns: https://unicode.org/charts/PDF/U2800.pdf (spinners)
- Terminal color standards: ANSI X3.64 / ISO/IEC 6429
- TouchDesigner textTOP docs: https://docs.derivative.ca/Text_TOP
