# Multi-Track Enrichment Schema

> Extension to basic YouTube transcript extraction: structured curation layer with 7 track types.
> Source: EDGA-179 enrichment campaign, May 2026.

## Overview

Basic transcript extraction captures **what** was said. Enrichment captures:
- **Why it matters** (context)
- **How it connects** (vault_connections)  
- **What to do with it** (track-specific actions)

## The 7 Tracks

| Track | Purpose | Chroma Collection | Vault Wing | Agent |
|-------|---------|-------------------|------------|-------|
| **knowledge** | General curation | unified_knowledge | 03-Knowledge | Scribe |
| **tool_workflow** | Tool install review | edgeless_toolkit | 06-Toolkit | Kilo/Beau |
| **people** | Network graph | network_graph | 09-People | Curator |
| **trading_intel** | Prediction signals | trading_patterns | 08-Trading | Pamela |
| **creative_seeds** | Generative art | generative_art | 11-Creative | Critic/Specimen |
| **code_patterns** | Snippet extraction | code_snippets | 15-Snippets | Kilo |
| **opportunity** | Business ideas | business_pipeline | 07-Business | Builder |

## Schema Structure

### Universal Fields (All Tracks)
```yaml
---
title: "Video Title"
source: youtube
url: https://www.youtube.com/watch?v=VIDEO_ID
channel: ChannelName
published: 2026-05-06
processed: 2026-05-06
kb_score: 12

# Enrichment Tier (0-3 scale)
enrichment_tier: 2  # 0=raw, 1=basic, 2=structured, 3=deep synthesis

# Track Tags (multi-tag array)
track_tags: [knowledge, tool_workflow]

# Universal Fields
context: |
  Why this video matters: specific problem it solves for your work
one_liner: "Single sentence tweet-length summary"
vault_connections:
  - [[Related-Note-1]]
  - [[Related-Note-2]]
summary: "Already extracted from transcript or generated"
---
```

### Track-Specific Payloads

```yaml
# tool_workflow example
tool_workflow:
  - name: "Effect-TS"
    context: "TypeScript functional programming library"
    install_status: queued
    edgeless_guide: planned
    tested: false

# people example  
people:
  - name: "Andrej Karpathy"
    context: "Mentioned as RLHF expert"
    connection_type: follow  # follow, collaborate, invite, debate
    relevance: "Directly relevant to Pamela trading RL"

# trading_intel example
trading_patterns:
  - topic: "Polymarket odds calculation"
    market: "us-election-2024"
    signal_type: arbitrage_opportunity
    pamela_action: analyze_position
```

## Scoring System

### Field Coverage (5 Universal)
| Field | Extraction | Curation |
|-------|------------|----------|
| summary | ✅ Auto (76%) | Auto-generate from transcript |
| enrichment_tier | ✅ Auto (41%) | Assign based on depth |
| one_liner | ⚠️ Semi (41%) | Needs synthesis |
| context | ❌ Manual (26%) | Requires judgment |
| vault_connections | ❌ Manual (79%*) | Requires knowledge graph |

*79% auto-generated `[[Channel]]` links, not meaningful bidirectional connections

### Bonus Scoring
- Base: 5 points (one per universal field)
- Track bonus: +1 per track with populated payload
- Max score: 5 + number_of_tracks (can exceed 5/5)

## Hybrid Detection

### Three-Layer Detection Stack
1. **Keyword matching** — Fast pattern matching on channel/title/body
2. **Transcript analysis** — NLP pattern detection in full text  
3. **ChromaDB clustering** — Semantic similarity to existing notes

### Keyword Patterns
```python
TOOL_PATTERNS = [
    r"(?:we|I)\s+(?:use|built|created|open sourced|released)\s+(\w+)",
    r"(?:npm|pip|cargo|brew)\s+install\s+(\S+)",
    r"(\w+)\s+(?:is a|provides|allows|enables)",
]

TRADING_PATTERNS = [
    r"(?:prediction market|odds|probability)\s+(?:of|for)\s+(\S+)",
    r"(?:Polymarket|Kalshi|predict)\s+(\S+)",
]

CREATIVE_PATTERNS = [
    r"(?:TouchDesigner|p5\.js|Processing|openFrameworks)",
    r"(?:shader|fragment|vertex|GLSL|HLSL)",
]
```

## Weekly Rhythm

### Phase 1: Assessment (15 min)
- Run `score_enrichment.py`
- Check dashboard: 10-Meta/yt-enrichment-panel.md
- Identify notes with score ≤3 (missing 2+ fields)

### Phase 2: Batch Enrichment (45-90 min)
- Process 20-50 notes
- Run track detection on each
- Populate missing universal fields
- Add track-specific payloads

### Phase 3: Knowledge Graph (30 min)
- Sync ChromaDB embeddings
- Create bidirectional vault connections
- Review emergent clusters

### Phase 4: Agent Handoffs (15 min)
- Route tool_workflow → Kilo
- Route knowledge → Scribe
- Route trading_intel → Pamela

## Implementation Files

| File | Purpose |
|------|---------|
| `scripts/youtube_intelligence/score_enrichment.py` | Score 5 fields across all notes |
| `scripts/youtube_intelligence/track_processors.py` | Detect tracks from transcript |
| `nightly_enrichment_backfill.py` | Create Paperclip issues for low-scored notes |
| `yt-enrichment-stats.json` | Live dashboard data |
| `youtube-enriched.md` (template) | Note template with conditional track sections |

## Gap Targets

| Metric | Current | 30-Day Target |
|--------|---------|---------------|
| Fully enriched | 22.9% | 30% |
| Context field | 26% | 50% |
| Tool workflow tags | 1.5% | 10% |
| Meaningful vault_connections | ~25% | 50% |
