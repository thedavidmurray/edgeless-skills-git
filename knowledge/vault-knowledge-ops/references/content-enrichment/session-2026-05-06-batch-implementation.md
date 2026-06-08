# Batch Track Detection Implementation — May 2026

Session: 2026-05-06  
Scope: Enrich 1,172 YouTube notes with multi-track tags  
Result: 885 notes updated, track coverage 1.5% → 38.8%

## Implementation Pattern

### Phase 1: Keyword-Based Fast Detection

For bulk operations (100+ notes), skip transcript API calls and use keyword matching:

```python
TRACK_KEYWORDS = {
    "tool_workflow": ["npm", "cargo", "pip", "brew", "install", "CLI", "uv", 
                      "Effect-TS", "Claude Code", "Docker", "vite", "webpack"],
    "people": ["interview", "conversation with", "featuring", "guest"],
    "trading_intel": ["Polymarket", "prediction market", "odds", "Kalshi"],
    "creative_seeds": ["TouchDesigner", "p5.js", "shader", "generative"],
    "code_patterns": ["pattern", "design pattern", "refactor", "idiomatic"],
    "opportunity": ["business idea", "startup", "someone should", "market gap"],
}

def assign_tracks_by_keywords(channel, title, body_sample):
    text = f"{channel} {title} {body_sample}".lower()
    tracks = ["knowledge"]  # Baseline
    
    for track, keywords in TRACK_KEYWORDS.items():
        if any(kw.lower() in text for kw in keywords):
            tracks.append(track)
    
    return list(set(tracks))  # Deduplicate
```

**Performance:** 1,157 notes processed in 26.8 seconds (vs. 30+ min for transcript fetch)

### Phase 2: Frontmatter Injection

Insert `track_tags` array into existing frontmatter:

```python
content = note_path.read_text()
lines = content.split('\n')

# Find frontmatter end
fm_end = 0
if lines[0].strip() == "---":
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            fm_end = idx
            break

# Insert before frontmatter end
tracks = assign_tracks_by_keywords(channel, title, body[:500])
lines.insert(fm_end, f"track_tags: {json.dumps(tracks)}")
note_path.write_text('\n'.join(lines))
```

### Phase 3: Routing to Agents

After tagging, create Paperclip issues for specialist agents:

| Track | Agent | Action | Queue Size |
|-------|-------|--------|------------|
| tool_workflow | Kilo | Install review | 380 items |
| trading_intel | Pamela | Trading pipeline | 144 items |
| code_patterns | Kilo | Snippet extraction | 57 items |
| creative_seeds | Critic | Creative library | 15 items |

## Results

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Notes with track_tags | 115 (9.8%) | 1,000 (86.4%) | +885 |
| tool_workflow items | 17 | 380 | +363 (21x) |
| trading_intel items | 3 | 144 | +141 (48x) |
| code_patterns items | 9 | 57 | +48 (6x) |
| Multi-track coverage | 1.5% | 38.8% | +37.3% |

## Key Learning

**Hybrid approach works best:**
- **Fast path (keywords):** For initial bulk enrichment (20% target)
- **Deep path (transcripts):** For Tier-3 enrichment with contextual analysis
- **ChromaDB clustering:** For emergent pattern detection (next phase)

## Pitfall Avoided

youtube-transcript-api v1.0.0+ uses `.text` attribute on snippet objects, not `["text"]` dict access. The skill's transcript-based detection needs this migration if using transcript fetch for deep analysis.

## Related

- `youtube-enrichment-decisions.md` — Strategy document
- `system-gap-analysis.md` — Gap analysis methodology
- `track_processors.py` — Detection implementation
