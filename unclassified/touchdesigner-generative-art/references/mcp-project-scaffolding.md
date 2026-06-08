# TD Project Scaffolding via twozero MCP

Complete pattern for building branded generative art projects programmatically via twozero MCP, based on Edgeless Hero Animation build (2026-04-29).

## Architecture Overview

```
Hermes → twozero MCP (HTTP 40404) → TouchDesigner
           ↓
    Create container → Add custom params → Build operator network
           ↓
    Wire with expressions → Brand integration → Export/recording
```

## Phase 1: Container with Custom Parameters

```python
# Create base container with control page enabled
td_create_operator(
    type="baseCOMP",
    parent="/project1",
    name="hero_base",
    parameters={"controlcomp": True}
)

# Add custom parameter page via Python
td_execute_python("""
hero = op('/project1/hero_base')
page = hero.appendCustomPage('ProjectParams')

# Animation controls
page.appendFloat('Seed', label='Seed', min=0, max=1000, default=42)
page.appendFloat('Speed', label='Speed', min=0.1, max=2.0, default=0.5)
page.appendFloat('Complexity', label='Complexity', min=1, max=20, default=8)

# Brand colors (Edgeless palette example)
page.appendRGB('Primarycolor', label='Primary')
page.appendRGB('Secondarycolor', label='Secondary')

# Set defaults
hero.par.Primarycolorr = 0.0      # Cyan
hero.par.Primarycolorg = 0.831
hero.par.Primarycolorb = 1.0

print('Custom parameters created')
""")
```

## Phase 2: Operator Network Construction

### CHOP Layer (Animation)
```python
# Time driver linked to Speed param
td_create_operator(type="speedCHOP", parent="/project1/hero_base", name="time_driver")
td_execute_python("""
op('/project1/hero_base/time_driver').par.speed.expr = 'parent().par.Speed'
""")

# Noise with evolving seed
td_create_operator(type="noiseCHOP", parent="/project1/hero_base", name="anim_noise")
td_execute_python("""
n = op('/project1/hero_base/anim_noise')
n.par.seed.expr = 'parent().par.Seed + int(absTime.seconds * 10)'
n.par.roughness.expr = 'parent().par.Complexity / 10'
""")
```

### SOP Layer (Geometry)
```python
# Grid for particle emission surface
td_create_operator(
    type="gridSOP",
    parent="/project1/hero_base",
    name="emission_grid",
    parameters={"rows": 32, "cols": 32, "size": (10, 10)}
)

# Noise displacement
td_create_operator(type="noiseSOP", parent="/project1/hero_base", name="displacer")

# Transform with orbital animation
td_create_operator(type="transformSOP", parent="/project1/hero_base", name="orbiter")
td_execute_python("""
t = op('/project1/hero_base/orbiter')
t.par.tx.expr = 'sin(absTime.seconds * parent().par.Speed) * 2'
t.par.ty.expr = 'cos(absTime.seconds * parent().par.Speed * 0.7) * 1'
t.par.rx.expr = 'absTime.seconds * 20 * parent().par.Speed'
""")
```

### TOP Layer (Post-processing)
```python
# Background noise
td_create_operator(
    type="noiseTOP",
    parent="/project1/hero_base",
    name="bg",
    parameters={"resolutionw": 1280, "resolutionh": 720, "type": "Perlin"}
)

# Color grade
td_create_operator(type="levelTOP", parent="/project1/hero_base", name="grade")

# Glow/blur
td_create_operator(
    type="blurTOP",
    parent="/project1/hero_base",
    name="glow",
    parameters={"size": 2, "type": "Gaussian"}
)
```

### COMP Layer (Rendering)
```python
# Geometry container
td_create_operator(
    type="geometryCOMP",
    parent="/project1/hero_base",
    name="scene",
    parameters={"geopath": "./orbiter"}
)

# Camera
td_create_operator(
    type="cameraCOMP",
    parent="/project1/hero_base",
    name="cam",
    parameters={"tx": 0, "ty": 0, "tz": 15, "rx": -15}
)

# Light with brand color
td_create_operator(
    type="lightCOMP",
    parent="/project1/hero_base",
    name="key_light",
    parameters={
        "lighttype": "Point",
        "tx": 5, "ty": 5, "tz": 5,
        "r": 0.0, "g": 0.831, "b": 1.0  # Cyan
    }
)

# Render TOP
td_create_operator(
    type="renderTOP",
    parent="/project1/hero_base",
    name="render",
    parameters={"resolutionw": 1280, "resolutionh": 720}
)
```

## Phase 3: Wiring Networks

### CHOP Chain
```python
td_execute_python("""
base = op('/project1/hero_base')
time_driver = base.op('time_driver')
anim_noise = base.op('anim_noise')

time_driver.outputConnectors[0].connect(anim_noise.inputConnectors[0])
""")
```

### SOP Chain
```python
td_execute_python("""
base = op('/project1/hero_base')
grid = base.op('emission_grid')
displacer = base.op('displacer')
orbiter = base.op('orbiter')

grid.outputConnectors[0].connect(displacer.inputConnectors[0])
displacer.outputConnectors[0].connect(orbiter.inputConnectors[0])

displacer.par.amplitude.expr = 'parent().par.Complexity / 4'
""")
```

### Render Setup
```python
td_execute_python("""
base = op('/project1/hero_base')
render = base.op('render')
render.par.camera = '../cam'
render.par.geometry = '../scene'
""")
```

## Phase 4: Brand Identity Integration

### Color Palette Enforcement
```python
# Material with brand colors
td_create_operator(
    type="phongMAT",
    parent="/project1/hero_base",
    name="brand_mat",
    parameters={
        "diffuse": (0.0, 0.831, 1.0),      # Cyan
        "specular": (0.616, 0.302, 0.867),  # Purple
        "ambient": (0.0, 0.2, 0.3)
    }
)
```

### Text Overlay with Identity
```python
td_create_operator(
    type="textTOP",
    parent="/project1/hero_base",
    name="identity_text",
    parameters={
        "text": "BRAND ██████ PROJECT ██████ SWARM",
        "fonttype": "Courier",  # Monospace = CLI/terminal aesthetic
        "fontsize": 24,
        "resolutionw": 1280,
        "resolutionh": 720,
        "color": (0.0, 1.0, 0.533),  # Green accent
        "bgalpha": 0.0
    }
)

# Animated timestamp
td_create_operator(
    type="textTOP",
    parent="/project1/hero_base",
    name="timestamp",
    parameters={
        "text": "2026-04-29 :: Hive#2662",  # Agent identity
        "fonttype": "Courier",
        "fontsize": 14,
        "color": (0.616, 0.302, 0.867),  # Purple
        "bgalpha": 0.0
    }
)

td_execute_python("""
# Position in corner
ts = op('/project1/hero_base/timestamp')
ts.par.translatex = 20
ts.par.translatey = 680
ts.par.alignx = 'left'
ts.par.aligny = 'bottom'

# Subtle float animation
id_text = op('/project1/hero_base/identity_text')
id_text.par.translatex.expr = '10 + sin(absTime.seconds * 0.5) * 5'
id_text.par.opacity.expr = '0.3 + 0.2 * absTime.frame % 60 / 60'
""")
```

## Phase 5: Output & Recording

```python
# Composite layer
td_create_operator(
    type="compositeTOP",
    parent="/project1/hero_base",
    name="final",
    parameters={"operation": "Over"}
)

# Output null
td_create_operator(type="nullTOP", parent="/project1/hero_base", name="out")

# Movie recorder
td_create_operator(
    type="moviefileoutTOP",
    parent="/project1/hero_base",
    name="recorder",
    parameters={
        "type": "movie",
        "videocodec": "prores",  # Non-commercial safe on macOS
        "file": "/Users/djm/Desktop/output.mov",
        "fps": 30
    }
)

# Wire final output
project = op('/project1')
project.par.output = '/hero_base/out'
```

## ASCII Aesthetic Patterns

### Grid Density Allusion
Use grid SOP dimensions to evoke terminal/ASCII art density:
- `rows=32, cols=32` = 1024 "characters"
- `rows=80, cols=25` = Classic terminal dimensions
- Visible grid lines = ASCII character cell boundaries

### Monospace Typography
Always `fonttype="Courier"` or `fonttype="Monaco"` for:
- Identity text
- Timestamps
- Parameter displays
- Debug overlays

### Block Character Separators
Use Unicode block characters in text:
- `█` (U+2588) Full block
- `▓` (U+2593) Dark shade
- `▒` (U+2592) Medium shade
- `░` (U+2591) Light shade

Example: `"PROJECT ▓▓▓▓▓▓ AGENT ▓▓▓▓▓▓ SWARM"`

### CLI-Style Timestamp
Format: `YYYY-MM-DD :: Agent#ID`
- Double colon `::` = CLI prompt convention
- Agent codename + number = swarm identity
- Fixed-width = monospace alignment

## Verification Steps

```python
# Check for errors
td_get_errors(path="/project1/hero_base", recursive=True)

# Take screenshot
td_get_screenshot(
    path="/project1/hero_base/out",
    output_path="/Users/djm/Desktop/verify.png"
)

# Check network structure
td_get_network(path="/project1/hero_base", depth=2)
```

## Parameter Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Animation | Verb/noun | `Speed`, `Complexity`, `Seed` |
| Color | Role-based | `Primarycolor`, `Accentcolor` |
| Identity | Brand-specific | `Logotext`, `Agentid` |
| Technical | Functional | `Resolutionw`, `Codec` |

## Common Pitfalls

1. **Expression syntax**: Use single quotes in Python f-strings for TD expressions
   - Wrong: `f"{speed}"` 
   - Right: `'parent().par.Speed'`

2. **Path references**: Always use `../` or `./` for relative paths in parameters

3. **Custom page**: Must set `controlcomp=True` on baseCOMP before adding params

4. **Resolution**: Non-commercial TD caps at 1280×1280. Use explicit resolution params.

## Integration with Swarm Agents

Specimen (Generative Art Producer) workflow:
```
1. Load this template via MCP
2. Parameter sweep (Seed 1-1000)
3. Screenshot frame 0 (thumbnail)
4. Vision model score
5. If score > 7.0: record full animation
6. Log to experiments.tsv
```

Critic (Creative Director) workflow:
```
1. Load renders from moviefileoutTOP
2. Evaluate via 55/45 algo/judge scoring
3. Check brand color compliance
4. Recommend parameter tuning
```
