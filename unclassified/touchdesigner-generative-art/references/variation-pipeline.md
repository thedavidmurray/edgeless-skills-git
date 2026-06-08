# TouchDesigner Variation Pipeline

Automated parameter sweep → vision scoring → champion selection → video rendering.

## Architecture

```
TD Template → Parameter Randomization → Screenshot → Vision Score → Champion Dir
                     ↓                                    ↓
              100 variations                       Score ≥ 7.0
                     ↓                                    ↓
              Manifest JSON                        300-frame render
```

## Pipeline Class

```python
class TDVariationPipeline:
    """Generate variations, score with vision, render champions."""
    
    def __init__(self, base_project: str, param_ranges: Dict[str, tuple]):
        self.base_project = base_project
        self.param_ranges = param_ranges  # {"Speed": (0.05, 0.5), ...}
        
    def generate_parameter_set(self, seed: int) -> Dict[str, float]:
        """Random params from ranges."""
        random.seed(seed)
        return {p: random.uniform(min, max) for p, (min, max) in self.param_ranges.items()}
    
    def set_parameters(self, params: Dict[str, float]) -> bool:
        """Execute Python in TD via MCP td_execute_python."""
        script = f"op('/project1/parameters').par.Speed = {params['Speed']}"
        return td_execute_python(script)
    
    def capture_screenshot(self, path: str) -> bool:
        """td_get_screenshot MCP tool."""
        pass
    
    def score_with_vision(self, image_path: str, criteria: str) -> float:
        """Call Nous Portal vision API. Returns 0-10."""
        pass
    
    def run_pipeline(self, n: int = 100) -> List[Dict]:
        """Full sweep: generate, capture, score, collect champions."""
        for seed in range(n):
            params = self.generate_parameter_set(seed)
            self.set_parameters(params)
            self.capture_screenshot(f"var_{seed:04d}.png")
            score = self.score_with_vision(...)
            if score >= 7.0:
                # Copy to champions/, queue for video render
                pass
        return results
    
    def render_champion_video(self, seed: int, frames: int = 300) -> str:
        """Full 10s video for champion variation."""
        params = self.generate_parameter_set(seed)
        self.set_parameters(params)
        # Start MovieFileOutTOP recording
        # Wait frames / 30fps seconds
        # Stop recording
        return "/tmp/champion_{seed:04d}.mov"
```

## Parameter Ranges by Template

| Template | Params | Ranges |
|----------|--------|--------|
| hero-flow | Speed, Roughness, Contrast | (0.05,0.5), (0.3,0.8), (0.8,1.5) |
| audio-reactive | Gain, Sensitivity, ColorShift | (5,15), (0.5,2.0), (0,1) |
| swarm-viz | BreathingRate, Scatter, GlowIntensity | (0.1,0.5), (0,1), (0.5,2.0) |

## Vision Scoring Criteria

```python
CRITERIA = "abstract,flowing,neon_palette,edgeless_aesthetic,professional_quality"
```

- `abstract` — Non-representational forms
- `flowing` — Smooth motion, no jarring
- `neon_palette` — Cyan/purple/green dominance
- `edgeless_aesthetic` — Brand alignment
- `professional_quality` — Production-ready

## Output Structure

```
captures/edgelesslab/
├── var_0000.png ... var_0099.png    # All screenshots
├── champions/                        # Score ≥ 7.0
│   ├── var_0007.png
│   ├── var_0012.png
│   └── ...
├── champion_0007.mov               # Full videos (300 frames)
├── champion_0012.mov
└── pipeline_manifest.json          # Full metadata
```

## Usage

```bash
# Generate 100 variations
python3 td_variation_pipeline.py hero -n 100

# Render champions only
python3 td_variation_pipeline.py hero --champions-only

# Specific template
python3 td_variation_pipeline.py audio -n 50
python3 td_variation_pipeline.py swarm -n 20 --champions-only
```

## Integration with Swarm

```markdown
#bot-backroom:
[FROM:Hive][TO:Hive][TYPE:ARCH][REF:EDGA-XXX]
Run TD pipeline: 100 hero variations, edgeless_aesthetic criteria.
Output: Top 10 champions to Discord + web assets dir.
```

Execution:
1. skill_view('touchdesigner-generative-art')
2. Load variation-pipeline.md reference
3. Execute pipeline
4. Post champions to #general
5. Update Paperclip issue with manifest

## Non-Commercial Constraints

- Resolution: 1280×720 (within 1280×1280 cap)
- Codec: ProRes or MJPA only
- No H.264/H.265/AV1 without Commercial license
- Use `outputresolution = 'custom'` + explicit dimensions
