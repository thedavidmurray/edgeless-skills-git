---
name: multi-track-content-enrichment
title: Multi-Track Content Enrichment System
description: Classify and enrich content into multiple semantic tracks for routing to specialist agents/workflows
tags: [enrichment, classification, routing, knowledge-management]
---

# Multi-Track Content Enrichment System

Classify incoming content (YouTube, RSS, podcasts, articles) into one or more semantic tracks, each triggering distinct downstream processing workflows.

## Core Concept

Content enters through a single ingestion point, gets analyzed for track membership via pattern detection or manual tagging, and routes to track-specific processors that create structured payloads for specialist agents.

## The 7 Standard Tracks

| Track | Purpose | Downstream Agent | Output |
|-------|---------|------------------|--------|
| **knowledge** | General learning & synthesis | Scribe | Vault note + NotebookLM |
| **tool_workflow** | Tool evaluation & installation | Kilo/Beau | Install review queue + Edgeless guide |
| **people** | Network building & collaboration | Curator | Network graph entries |
| **trading_intel** | Market signals & predictions | Pamela | Trading pipeline feed |
| **creative_seeds** | Generative art techniques | Critic/Specimen | Creative library entries |
| **code_patterns** | Reusable code snippets | Kilo | Skill library candidates |
| **opportunity** | Business/product ideas | Builder | Opportunity pipeline |

## Schema Structure

### Frontmatter (Universal Fields)
```yaml
enrichment_tier: 3  # 0-3 scale
track_tags: [knowledge, tool_workflow]  # multi-tag array
context: "Why this matters to you"
one_liner: "Tweet-length summary"
vault_connections: [[Related-Note-1]], [[Related-Note-2]]
```

### Track-Specific Payloads
```yaml
tool_workflow:
  - name: "uv"
    context: "Python packaging tool"
    install_status: queued
    edgeless_guide: planned
    
people:
  - name: "Andrej Karpathy"
    connection_type: follow  # follow, collaborate, invite, debate
    relevance: "RLHF expertise for Pamela"
```

## Scoring Formula

```
Score = universal_fields (max 5) + track_payloads (1 per populated track)
```

A note with all 5 universal fields + 2 track payloads = score 7/5 (displayed as "5+ enrichment")

## Pattern Detection

Each track has regex patterns for auto-detection from transcripts:

- **tool_workflow**: `npm install`, `cargo install`, "we built X", "check out Y"
- **people**: "follow X", "interview with Y", "shout out to Z"
- **trading_intel**: "prediction market", "Polymarket", "implied probability"
- **creative_seeds**: "TouchDesigner", "shader", "generative art", "Perlin noise"
- **code_patterns**: Code blocks (```lang), "design pattern", "idiomatic"
- **opportunity**: "someone should build", "market gap", "no one is doing"

## Implementation

### 1. Detection Phase
```python
from track_processors import suggest_tracks

suggested = suggest_tracks(note_path, video_id)
# Returns: ['knowledge', 'tool_workflow', 'code_patterns']
```

### 2. Enrichment Phase
```python
payloads = run_track_detection(note_path, video_id)
for p in payloads:
    print(f"{p.track}: {p.action_recommended}")
```

### 3. Routing Phase
Based on `action_recommended`:
- `create_install_review_queue` → Paperclip issue for Kilo
- `add_to_network_graph` → Curator agent task
- `feed_to_pamela_pipeline` → Trading analysis queue
- `add_to_creative_library` → Critic/Specimen review
- `extract_to_snippet_library` → Skill library PR
- `add_to_business_pipeline` → Builder opportunity queue

## Adding a New Track (Track 8+)

1. Add to `TRACK_PAYLOAD_FIELDS` mapping
2. Create `process_new_track()` function with detection patterns
3. Register in `TRACK_PROCESSORS` dict
4. Create ChromaDB collection for semantic clustering
5. Update template with conditional section

## Integration with ChromaDB

Track assignment feeds into semantic clustering:
- Notes cluster by content similarity within tracks
- Emergent clusters suggest new track creation (hybrid approach)
- Cross-track connections discovered via embedding similarity

## Pitfalls

- **youtube-transcript-api v1.0.0+**: Uses `.text` attribute on snippets, NOT `["text"]` dict access. See `references/youtube-transcript-api-v1-migration.md` for full migration guide.
- **Bulk enrichment speed**: When processing 100+ notes, use keyword-based track assignment instead of transcript fetching for speed. Reserve transcript analysis for Tier-3 enrichment.
- **Score calculation**: Track payload bonuses can push scores above 5. Display as "5+" or "5/N" format, not literal integers.
- **Multi-tag deduplication**: Always `list(set(tracks))` before writing to avoid duplicate track tags from overlapping pattern matches.

## Bulk Enrichment Pattern

For efficiently enriching 100+ notes (reaches 20% target quickly):

```python
# Fast-path: Skip transcript fetch, use channel/title keywords
TRACK_KEYWORDS = {
    "tool_workflow": ["claude code", "cargo", "npm", "docker", "uv"],
    "creative_seeds": ["touchdesigner", "shader", "generative", "p5.js"],
    "trading_intel": ["polymarket", "prediction", "market"],
    "code_patterns": ["rust", "pattern", "idiomatic"],
    "opportunity": ["startup", "gap", "someone should"],
}

def assign_tracks_by_keywords(channel, title):
    text = f"{channel} {title}".lower()
    tracks = ["knowledge"]
    for track, keywords in TRACK_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            tracks.append(track)
    return list(set(tracks))

# Then fill all 5 universal fields in one write
new_fm["track_tags"] = assign_tracks_by_keywords(channel, title)
new_fm["context"] = f"YouTube: {title} from {channel}"
new_fm["one_liner"] = f"Explores {title}"
new_fm["enrichment_tier"] = "2"
new_fm["vault_connections"] = [f"[[{channel}]]"]
new_fm["summary"] = f"Video on {title}"
```

This pattern enriched 154 notes in <1 second vs. 30+ minutes for transcript-based detection.

## Reference Files

- `references/session-2026-05-06-batch-implementation.md` — Production-scale batch enrichment session results (885 notes, 26s, +37% coverage)
- `references/youtube-transcript-api-v1-migration.md` — API migration guide for transcript-based detection