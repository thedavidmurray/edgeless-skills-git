---
name: signal-extraction-layer
description: >
  Signal Extraction Layer (SEL) - Generalized pattern for extracting structured 
  insights from any source. Transforms whole-content scoring into granular signal 
  capture across YouTube, RSS, Paperclip, agent outputs, and KB articles.
version: 1.0.0
author: Beau (Paperclip Agent)
metadata:
  tags: [signal-extraction, knowledge-management, architecture, chromadb, money-lab-generalization]
  tier: task-specific
  domain: devops
  color: indigo
  dependencies: [chromadb]
---

# Signal Extraction Layer (SEL)

## Purpose

**The Problem:** Whole-content scoring throws away granular signal. Money Lab (YouTube) captures revenue mechanics, but the same pattern applies everywhere we score-then-discard.

**The Solution:** Generalize Money Lab into a reusable primitive - the Signal Extraction Layer. Extract structured, queriable insights from any source.

## Core Abstraction: The Signal

```python
class Signal(BaseModel):
    id: str                    # deterministic from source + content hash
    category: str              # signal type (revenue-mechanic, decision, gotcha, etc.)
    sub_tags: list[str]        # additional tags
    quote: str                 # exact source content
    paraphrase: str            # concise extraction
    confidence: float          # 0-1 extraction confidence
    source: SourceRef          # {kind, identifier, url, location_hint}
    extracted_by: str          # extractor version
    extracted_at: datetime
```

## Source Extractors

| Source | Categories | Location |
|--------|-----------|----------|
| YouTube likes | revenue-mechanic, service-offering, stack, outbound, pricing, self-publishing, tool-ref | `extractors/youtube_likes.py` |
| RSS articles | tools-mentioned, pricing-data, vendor-moves, regulatory, market-stats | `extractors/rss_feeds.py` |
| Paperclip done issues | decision, lesson-learned, gotcha, reusable-pattern | `extractors/paperclip_done_issues.py` ✓ |
| Agent heartbeats | finding, anomaly, blocker, surprise | `extractors/agent_heartbeats.py` |
| KB articles | framework, formula, claim, methodology | `extractors/kb_articles.py` |
| Discord activity | pattern, recurring-question, swarm-blocker | `extractors/discord_activity.py` |

## Storage

**Dual storage model:**
1. **Vault** (primary): `claude-vault/03-Knowledge/Signals/<source>/<category>/<id>.json`
2. **ChromaDB** (search): `signals` collection with embeddings for semantic retrieval

## CLI Usage

```bash
# Query across all sources
signals query "pricing models for AI services"

# Filter by source
signals query --source paperclip "lessons learned"

# Filter by category
signals query --category gotcha "authentication"

# Output as JSON
signals query --json "revenue mechanics" | jq '.[].confidence'
```

## Implementation Status

| Component | Status | Notes |
|-----------|--------|-------|
| Core schema | ✓ Complete | `core/schema.py` |
| Paperclip extractor | ✓ Complete | 695 signals extracted |
| ChromaDB collection | ✓ Created | `signals` collection exists |
| Vault storage | ✓ Complete | 695 files written |
| YouTube extractor | ⏳ Planned | Needs Money Lab integration |
| RSS extractor | ⏳ Planned | Depends on RSS pipeline |
| Agent heartbeat extractor | ⏳ Planned | Needs heartbeat log parsing |
| Unified CLI | ✓ Basic | Simple text search implemented |
| Embedding search | ⏳ Planned | Requires embedding pipeline |

## Key Files

```
~/.hermes/skills/signal-extraction-layer/
├── core/
│   └── schema.py           # Signal and SourceRef models
├── extractors/
│   └── paperclip_done_issues.py  # Paperclip done issues extractor
├── cli/
│   └── signals.py          # Query CLI
└── SKILL.md               # This file
```

## Acceptance Criteria (from EDGA-964)

- [x] Generic `Signal` schema + `signals` ChromaDB collection
- [x] At least 1 source extractor implemented (Paperclip done issues: 695 signals)
- [ ] At least 3 source extractors implemented
- [x] Unified retrieval CLI: `signals query "..."`
- [ ] Signals appear in weekly drift-audit
- [ ] Backfill across at least 90 days of historical data per source

## Why This Is Structural

Money Lab = 1 extractor. SEL = architecture that makes Money Lab + Paperclip-Lessons + Agent-Findings + KB-Frameworks + RSS-Tools all work the same way. Without it, every "let's extract X from Y" becomes a one-off project.

## Owner

Edgeless CC (architecture + schema) + Hive (per-source extractors, depth-worker) per original issue spec. Implementation by Beau.

## Related

- EDGA-953/954/955 (Money Lab - first concrete extractor)
- EDGA-964 (This SEL implementation)
- `claude-vault/03-Knowledge/Signals/` (vault storage)
