# Edgeless Hero Animation Template

**Use for:** Generative brand animations, swarm visualizations, ASCII-aesthetic projects  
**Components:** 3D swarm geometry + postFX + text overlays + color palette  
**Created:** 2026-04-29 Edgeless Hero project  
**Operators:** ~20 (CHOPs, SOPs, TOPs, COMPs, MATs)

## Architecture

```
CHOP Animation → SOP Geometry → TOP PostFX → Text Overlays → Output
```

### Layer Breakdown

| Layer | Operators | Purpose |
|-------|-----------|---------|
| **Animation** | time_driver, swarm_noise, pulse_lfo, signal_blend | Organic motion |
| **Geometry** | ascii_grid, grid_displace, particle_sphere, swarm_transform | 3D swarm |
| **Rendering** | swarm_geo, hero_cam, edgeless_light, edgeless_mat | 3D → 2D |
| **PostFX** | bg_noise, color_grade, edge_glow | Background atmosphere |
| **Text** | ascii_overlay, timestamp_text | Brand identity |
| **Composite** | scene_comp, final_comp, hero_out | Layer stacking |

## Color Palette (Edgeless Brand)

```python
CYAN = (0.0, 0.831, 1.0)       # Primary: #00D4FF
PURPLE = (0.616, 0.302, 0.867) # Secondary: #9D4EDD  
GREEN = (0.0, 1.0, 0.533)      # Accent: #00FF88
```

## Key Parameters to Expose

On `baseCOMP` custom parameter page:

| Param | Type | Range | Default | Effect |
|-------|------|-------|---------|--------|
| `Seed` | Float | 0-1000 | 42 | Noise randomization |
| `Speed` | Float | 0.1-2.0 | 0.5 | Animation tempo |
| `Complexity` | Float | 1-20 | 8 | Displacement amplitude |
| `Swarmcount` | Float | 10-500 | 100 | Particle density |
| `Asciiintensity` | Float | 0-1 | 0.3 | Text glow |

## Wiring Order (Critical)

CompositeTOP inputs must be wired in sequence:

```python
# 0: Background
glow.outputConnectors[0].connect(scene_comp.inputConnectors[0])

# 1: 3D render  
render.outputConnectors[0].connect(scene_comp.inputConnectors[1])

# 2: (if needed) Additional layer
# scene_comp.outputConnectors[0].connect(final_comp.inputConnectors[0])
```

**"Not enough sources" error** = skipped input slot or wrong order.

## Camera Positioning

Default `tz=15` is often too far for small geometry:

```python
# Adjust after creation
hero_cam.par.tz = 5      # Move closer
hero_cam.par.rx = -15    # Look down slightly
hero_cam.par.ry = 10     # Angle offset
```

## TextTOP ASCII Style

```python
{
    "resolutionw": 1280,
    "resolutionh": 720,
    "font": "Courier",           # Monospace for ASCII feel
    "fontsizex": 48,
    "fontsizexunit": "pixels",
    "alignx": "left",
    "aligny": "bottom",
    "positionx": 0.05,          # Normalized coordinates
    "positiony": 0.05,
    "positionunit": "fraction",
    "fontcolorr": 0.0,           # Edgeless green
    "fontcolorg": 1.0,
    "fontcolorb": 0.533,
    "fontalpha": 1.0,
    "bgalpha": 0.0,              # CRITICAL: transparent
    "text": "EDGELESS ██████ HERMES ██████ SWARM"
}
```

## Debugging by Screenshot Size

| Size | Meaning |
|------|---------|
| 2-4 KB | Empty/black — check connections |
| 5-10 KB | Partial — check composite inputs |
| 60-70 KB | Working — full noise/glow visible |

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Black 3D render | Camera too far | `hero_cam.par.tz = 5` |
| Text not visible | `bgalpha` not 0 | Set `bgalpha=0.0` |
| "Not enough sources" | Composite order wrong | Wire 0, then 1, then 2 |
| Parameters wrong | Guessed names | Use `td_get_par_info` |

## Animation Export

```python
recorder = op('/project1/hero_base/hero_recorder')
recorder.par.record = True   # Start
# Wait duration...
recorder.par.record = False  # Stop
```

Output: `~/Desktop/edgeless_hero_animation.mov`

## MCP Build Script

See `scripts/build_edgeless_hero.py` for full automation.
