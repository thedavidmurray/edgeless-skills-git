---
name: touchdesigner-generative-art
description: Run TouchDesigner for real-time generative art, procedural animation, and audio-reactive visuals. Execute .toe projects headlessly, parameter sweeps, and live OSC control.
version: 1.0.0
author: Edgeless
related_skills:
  - autoreason-skill: Multi-candidate deliberative reasoning for selecting best TD outputs
  - autoresearch-loop: Iterative improvement harness for TD template quality
  - p5js: Procedural geometry generation that can feed into TD
  - manim-video: Math animation that can be stylized in TD
  - pixel-art: TD renders can be processed through pixel art pipelines

metadata:
  hermes:
    tags: [creative, generative-art, touchdesigner, procedural, animation, realtime]
    requires_telemetry: false
    required_environment:
      - TOUCHDESIGNER_PATH: Path to TouchDesigner executable
    install_check: |
      #!/bin/bash
      if [[ "$OSTYPE" == "darwin"* ]]; then
        TD_PATH="/Applications/TouchDesigner.app/Contents/MacOS/TouchDesigner"
      else
        TD_PATH="/c/Program Files/Derivative/TouchDesigner/bin/TouchDesigner.exe"
      fi
      [ -f "$TD_PATH" ] && echo "installed" || echo "not_installed"

---

# TouchDesigner Generative Art Skill

Run TouchDesigner programmatically through Hermes for automated generative art pipelines.

## Prerequisites

### Installation

**macOS:**
```bash
# Download from derivative.ca
open https://derivative.ca/download

# Or use Homebrew (community formula)
brew install --cask touchdesigner
```

**Windows:**
```powershell
# Download installer
Invoke-WebRequest -Uri "https://derivative.ca/download" -OutFile "td_installer.exe"
# Run installer
```

**Verify Installation:**
```bash
hermes touchdesigner check
```

### Environment Configuration

Add to your shell profile:
```bash
# macOS
export TOUCHDESIGNER_PATH="/Applications/TouchDesigner.app/Contents/MacOS/TouchDesigner"

# Windows (Git Bash/WSL)
export TOUCHDESIGNER_PATH="/c/Program Files/Derivative/TouchDesigner/bin/TouchDesigner.exe"
```

Or configure via Hermes:
```bash
hermes config set touchdesigner.path "/Applications/TouchDesigner.app/Contents/MacOS/TouchDesigner"
```

## Usage

### 1. Render a Project

```bash
hermes touchdesigner render \
  --project /path/to/art_project.toe \
  --output /output/generative_art.mp4 \
  --frames 300 \
  --params "seed=42,speed=0.5,color=#FF6B35"
```

**Parameters:**
- `--project`, `-p`: Path to .toe file (required)
- `--output`, `-o`: Output file path (.mp4, .mov, .png sequence)
- `--frames`, `-f`: Number of frames to render (default: 300)
- `--fps`: Frames per second (default: 30)
- `--params`: Comma-separated key=value parameter injection
- `--resolution`: Output resolution (default: 1920x1080)
- `--quiet`, `-q`: Suppress TouchDesigner GUI

### 2. Batch Parameter Sweeps

```bash
hermes touchdesigner iterate \
  --project /templates/noise_flow.toe \
  --param seed \
  --range 1-100 \
  --output_dir /art/variations/ \
  --parallel 4
```

Generates 100 variations with different seed values.

### 3. Create From Template

```bash
hermes touchdesigner create \
  --template noise_flow \
  --output /projects/my_flow.toe \
  --params "palette=neon,complexity=high"
```

**Available Templates:**
- `noise_flow` — Perlin noise particle flows
- `fractal_mountains` — 3D terrain generation
- `audio_reactive` — Sound-reactive geometry
- `shader_playground` — GLSL fragment shaders
- `data_viz` — Procedural data visualization
- `glitch_art` — Datamoshing, pixel sorting
- `particle_systems` — Physics-based particles
- `geometry_morph` — Shape interpolation

### 4. Live OSC Mode

```bash
hermes touchdesigner live \
  --project /projects/reactive_visuals.toe \
  --osc-port 7000 \
  --duration 3600
```

Starts TouchDesigner with OSC control enabled for real-time manipulation.

**OSC Control Examples:**
```bash
# Send parameter updates
hermes touchdesigner osc-send --port 7000 --address "/speed" --value 0.8
hermes touchdesigner osc-send --port 7000 --address "/color" --value "#FF6B35"
```

### 5. Integration with Autoreason

```python
# In a Hermes skill or script
from hermes_tools import touchdesigner

# Generate variations
for i in range(10):
    output = touchdesigner.render(
        project="/templates/noise_flow.toe",
        output=f"/output/variation_{i:03d}.mp4",
        params=f"seed={i},intensity={0.5 + i*0.05}",
        frames=150
    )
    
    # Evaluate with vision model
    score = evaluate_aesthetic(output)
    
    if score > 8.0:
        champion_variations.append(output)
```

## Project Structure

### Template .toe Files

Templates should expose parameters via:
- **Custom Parameters** on Base COMPs
- **Table DATs** for configuration
- **File In DATs** for external control

**Example Template Pattern:**
```
/project
  /base_generator (Base COMP)
    - Custom Par: seed (float)
    - Custom Par: speed (float)
    - Custom Par: color (RGB)
  /noise1 (Noise TOP) ← receives seed, speed
  /ramp1 (Ramp TOP) ← receives color
  /composite (Composite TOP)
  /movieout (Movie File Out TOP)
```

### Parameter Injection

Hermes writes to a JSON file that TouchDesigner reads:

```json
{
  "seed": 42,
  "speed": 0.5,
  "color": [1.0, 0.42, 0.21],
  "complexity": 8
}
```

TouchDesigner **File In DAT** watches this file and updates parameters.

## Advanced Patterns

### Pattern 0: MCP-Based Project Scaffolding

Build complete TD projects programmatically via twozero MCP without touching the GUI:

```bash
# See full pattern in references/mcp-project-scaffolding.md
# Includes: custom parameters, operator networks, brand integration, ASCII aesthetics
```

**Key capabilities:**
- Create baseCOMP containers with custom parameter pages
- Build CHOP/SOP/TOP/COMP networks via `td_create_operator`
- Wire connections with `td_execute_python`
- Add brand identity (colors, typography, logos)
- Export screenshots and video programmatically

**Use when:** You need to generate 10+ project variations, integrate with swarm agents (Specimen/Critic), or enforce brand consistency across renders.

### Pattern 1: ASCII Aesthetic in TouchDesigner

Evoke terminal/CLI aesthetics through TD visuals:

**Typography:**
```python
# Always monospace for identity elements
text_op.par.fonttype = "Courier"  # or "Monaco", "Consolas"

# CLI-style timestamp format — double colon notation
identity_text = "2026-04-29 :: Hive#2662"  # YYYY-MM-DD :: Agent#ID
```

**Grid Density Allusion:**
```python
# 32×32 = 1024 "character cells" — visible grid = ASCII cell boundaries
grid_sop.par.rows = 32
grid_sop.par.cols = 32

# Classic terminal dimensions: 80×25
grid_sop.par.rows = 25
grid_sop.par.cols = 80
```

**Block Character Separators:**
```python
# Unicode block characters in textTOP
text_op.par.text = "BRAND ██████ PROJECT ▓▓▓▓▓▓ SWARM"
# █ U+2588 Full block | ▓ U+2593 Dark shade | ▒ U+2592 Medium shade | ░ U+2591 Light shade
```

**Color Palette (Terminal Evocation):**
- Cyan (#00D4FF) = Primary terminal color
- Green (#00FF88) = Success/positive
- Purple (#9D4EDD) = Secondary accents
- Black background = Terminal default

**Motion Patterns:**
- Subtle text float (1-3px) = cursor blink/activity
- Character-by-character reveal = typing effect
- Scan lines/CRT overlay = retro terminal feel

### Pattern 2: Autoreason Loop with TD

```
┌─────────────────────────────────────────────────────────────────────┐
│  FOR i IN range(100):                                              │
│    1. Hermes generates random params                                │
│    2. TD renders frame 0 (thumbnail)                               │
│    3. Vision model scores aesthetic                                 │
│    4. If score > 7.0: TD renders full animation                    │
│    5. Curator selects top 10 for final                              │
└─────────────────────────────────────────────────────────────────────┘
```

### Pattern 2: Audio-Reactive Trading Visualization

```
┌─────────────────────────────────────────────────────────────────────┐
│  Pamela trading bot → Market data                                   │
│           ↓                                                        │
│  Hermes processes → OSC messages                                    │
│           ↓                                                        │
│  TD live project (shader) → Real-time reactive art                  │
│           ↓                                                        │
│  Stream to Twitch/YouTube                                          │
└─────────────────────────────────────────────────────────────────────┘
```

### Pattern 3: Book Animation Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│  Spread 1 static image (PNG)                                        │
│           ↓                                                        │
│  TD adds parallax layers, particle effects                          │
│           ↓                                                        │
│  Export: 5-second MP4 per spread                                  │
│           ↓                                                        │
│  Hermes assembles: Final motion book video                          │
└─────────────────────────────────────────────────────────────────────┘
```

### Pattern 3a: FFmpeg Fallback for Static Assets (No TD Automation)

When TouchDesigner headless automation isn't configured, use FFmpeg to create animated video from static character/scene images with subtle motion effects:

**Pipeline:**
```
character.png + audio.mp3 → FFmpeg zoompan → MP4 with narration
```

**Step 1: Create Animated Video from Static Image**
```bash
# 5-second video with subtle Ken Burns zoom effect
ffmpeg -y -loop 1 -i character.png \
  -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1" \
  -c:v libx264 -t 5 -pix_fmt yuv420p \
  -movflags +faststart \
  animated_spread.mp4
```

**Step 2: Add Audio Narration with Fade Effects**
```bash
# Combine video with audio narration
ffmpeg -y \
  -i animated_spread.mp4 \
  -i narration.mp3 \
  -filter_complex "[1:a]afade=t=in:ss=0:d=0.5,afade=t=out:ss=4:d=0.5[a]" \
  -map 0:v -map "[a]" \
  -c:v copy \
  -c:a aac -b:a 192k \
  -shortest \
  final_spread.mp4
```

**Batch Script for 16 Spreads:**
```bash
#!/bin/bash
# batch_spread_render.sh

CHAR_DIR="./characters"
AUDIO_DIR="./audio/narration"
OUTPUT_DIR="./renders"

for i in $(seq -w 1 16); do
  char_file="${CHAR_DIR}/spread_${i}_character.png"
  audio_file="${AUDIO_DIR}/spread_${i}_narration.mp3"
  output_file="${OUTPUT_DIR}/spread_${i}_final.mp4"
  
  # Skip if assets missing
  [ ! -f "$char_file" ] && continue
  [ ! -f "$audio_file" ] && continue
  
  # Create animated video
  ffmpeg -y -loop 1 -i "$char_file" \
    -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1" \
    -c:v libx264 -t 5 -pix_fmt yuv420p \
    /tmp/spread_video.mp4
  
  # Add audio
  ffmpeg -y -i /tmp/spread_video.mp4 -i "$audio_file" \
    -filter_complex "[1:a]afade=t=in:ss=0:d=0.5,afade=t=out:ss=4:d=0.5[a]" \
    -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest \
    "$output_file"
  
  echo "Spread $i: $output_file"
done
```

**When to Use FFmpeg Fallback:**
- TouchDesigner GUI automation not yet configured
- Quick proof-of-concept before full TD pipeline
- Rendering on headless VPS without GPU
- Batch processing many spreads with simple motion

**Limitations vs. Full TD:**
- No particle systems or complex effects
- No audio-reactive visuals
- Single-layer motion only
- No real-time parameter adjustment

**Transition Path:** Once TD headless automation is configured, replace FFmpeg `zoompan` with TD `noise` CHOPs, `transform` SOPs, and `particle` systems for richer animation.

## Error Handling

Common issues:

| Issue | Solution |
|-------|----------|
| "Codec not found" | Install FFmpeg, use `-codec H264` |
| "License expired" | TouchDesigner requires internet for license check |
| "GPU out of memory" | Reduce resolution, simplify project |
| "File not found" | Check TOUCHDESIGNER_PATH env var |
| "Parameters not updating" | Verify File In DAT path matches Hermes output |

## Integration with Other Skills

```
p5js → (export geometry) → TouchDesigner → (render) → pixel-art
            ↓                                              ↓
      procedural meshes                            final output
```

```
manim-video → (math animation) → TouchDesigner → (stylize) → baoyu-comic
              ↓                                              ↓
        base animation                              rendered frames
```

## References

| File | Description |
|------|-------------|
| `references/variation-pipeline.md` | Automated sweep → score → champion pipeline |
| `references/mcp-project-scaffolding.md` | Programmatic TD project construction via twozero MCP |

## Resources

- **TouchDesigner Docs:** https://docs.derivative.ca/
- **Command Line:** https://docs.derivative.ca/Command_Line_Arguments
- **Python API:** https://docs.derivative.ca/TouchDesigner_Python
- **Templates Library:** https://github.com/derivative-ca/TouchDesigner-Resources

## Examples

### Generate 100 Variations and Filter

```bash
# Generate
hermes touchdesigner iterate \
  --project /templates/noise_flow.toe \
  --param seed --range 1-100 \
  --output_dir /tmp/variations/ \
  --frames 1  # Just thumbnails

# Evaluate with vision model (automated)
hermes vision batch-evaluate \
  --input /tmp/variations/ \
  --output /art/champions/ \
  --criteria "abstract,flowing,neon_palette" \
  --threshold 8.0

# Render full animations for champions only
for f in /art/champions/*.toe; do
  hermes touchdesigner render \
    --project "$f" \
    --output "/art/final/$(basename $f .toe).mp4" \
    --frames 300
done
```

## Roadmap

- [ ] Template library (10 starter projects)
- [ ] OSC bridge for real-time control
- [ ] Integration with p5js/Three.js workflows
- [ ] Cloud render support (AWS GPU instances)
- [ ] NFT metadata generation pipeline
