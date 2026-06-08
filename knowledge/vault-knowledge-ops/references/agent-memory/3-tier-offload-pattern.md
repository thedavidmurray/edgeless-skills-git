---
title: Agent Memory 3-Tier Architecture & Offload Pattern
created: 2026-05-21
updated: 2026-05-21
type: reference
tags: [memory-management, agent-ops, chromadb, obsidian, memory-tiering, offload]
---

# Agent Memory 3-Tier Architecture

> Session-established pattern for managing agent working memory across HOT, WARM, and COLD storage tiers.
> Prevents MEMORY.md (20K) from becoming a bottleneck while leveraging existing infrastructure.

## The Three Tiers

| Tier | Storage | Capacity | What Goes There | What Does NOT Go There |
|------|---------|----------|-----------------|----------------------|
| **HOT** | MEMORY.md | 20,000 chars | Active blockers, provider health, auth status, agent config drift, recent decisions affecting next 3 turns | Historical context, completed work, pipeline details, code examples, enrichment workflows, incident post-mortems |
| **WARM** | ChromaDB | ~6,300+ docs, 22 collections | KB articles, technical specs, research summaries, code patterns, agent behaviors, debug solutions | Operating status, current blockers, provider credentials, session-to-session state |
| **COLD** | Obsidian Vault | 2.6GB, 5,144+ files | Design systems, reports, archived projects, visual bibles, source references, full SOPs, incident reports, agent behavior patterns | Anything needing <2 second retrieval, anything that changes every session |

## Offload Trigger Conditions

Offload from MEMORY.md → vault/ChromaDB when ANY of these are true:

1. **Capacity**: MEMORY.md exceeds 90% (18,000/20,000 chars)
2. **Staleness**: Entry describes a completed/resolved state and is >7 days old
3. **Wrong tier**: Entry is a detailed incident report, migration log, or behavior pattern — these belong in COLD vault with YAML frontmatter
4. **Duplication**: Same pattern described in 2+ memory entries (consolidate to single vault page)
5. **Reference weight**: Entry is primarily a pointer to files/paths that don't change (e.g., "EDGA-115 implementation lives at X") — keep pointer in MEMORY.md, move detail to vault

## Offload Workflow

### Step 1: Identify Candidates
Scan MEMORY.md for entries matching trigger conditions above. Priority order:
- Longest entries first (biggest impact)
- Completed incidents/migrations second
- Stable reference patterns third

### Step 2: Write Vault Pages
For each candidate, create a vault page under appropriate 03-Knowledge/ subdirectory:

```yaml
---
title: <Human-readable title>
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: concept | entity | reference
tags: [from vault taxonomy]
sources: [MEMORY.md]
confidence: high | medium | low
---
```

Page should contain FULL detail that was in MEMORY.md entry. Cross-link to related vault pages via `[[wikilinks]]`.

### Step 3: Create Index
If offloading 3+ related pages, create `index.md` in the subdirectory:

```markdown
# <Topic> Memory Offload
> Agent operational knowledge offloaded from MEMORY.md (20K limit) to vault.
> For current blockers and session-to-session state, check MEMORY.md.
> Last updated: YYYY-MM-DD | Total pages: N

## Pages
| Page | Type | Summary |
```

### Step 4: Replace MEMORY.md Entries
Replace each offloaded entry with a compact pointer:

```
<Short topic>: See `claude-vault/03-Knowledge/<path>/<page>.md`. <One-line summary of key fact>.
```

**Pointer length target:** <150 chars. Should be just enough to remind the agent the vault page exists.

### Step 5: Add Architecture Meta-Entry
After offload, add/update the meta-entry in MEMORY.md:

```
Memory architecture 3-tier (YYYY-MM-DD): MEMORY.md is HOT tier (20K) — active blockers, current auth status, provider health, recent decisions only. WARM tier: ChromaDB (~N docs, N collections) for semantic search of KB articles, technical specs, patterns. COLD tier: Obsidian vault (N GB, N files in 03-Knowledge/) for canonical long-form, source references, archived projects. Heavy operational patterns offloaded to `claude-vault/03-Knowledge/<subdir>/` (N pages with index). Read index.md there before re-deriving any agent behavior pattern.
```

## Canonical Offload Subdirectories

| Topic | Vault Path |
|-------|-----------|
| Agent behavior patterns | `03-Knowledge/Agent-Infrastructure/hive-memory-offload/` |
| Trading system details | `03-Knowledge/Trading/Pamela/` |
| Discord/swarm ops | `03-Knowledge/Agent-Infrastructure/` |
| Infrastructure incidents | `03-Knowledge/Agent-Infrastructure/` |
| Design system specs | `03-Knowledge/Design/` |
| Content enrichment workflows | `03-Knowledge/Content-Ops/` |

## Capacity Monitoring

Approximate capacity check (no special tooling needed):
- MEMORY.md injected into every turn — if it's >90%, new facts start getting rejected or existing ones get silently truncated
- Target headroom: 10-15% (2,000-3,000 chars) for session-specific facts
- When headroom drops below 5% (1,000 chars), perform emergency offload of the 5 largest entries immediately

## ChromaDB as WARM Tier — Usage Pattern

Before every substantive task: ONE ChromaDB query on the topic. Read top hits.
After every substantive task: write to vault (>200 words) or MEMORY.md (≤200 chars) with cross-link.

ChromaDB collections relevant to agent ops:
- `hermes_learnings` — tool errors, fixes, workarounds
- `agent-patterns` — agent behaviors, protocols, interactions
- `debug_solutions` — debugging paths and resolutions
- `project_knowledge` — project-specific context
- `code_patterns` — reusable code snippets
- `youtube_transcripts` — content source material

## Pitfalls

- **Pointer bloat**: Replacing a 400-char entry with a 300-char pointer saves almost nothing. Either write a <150 char pointer or don't bother.
- **Offload without index**: 9 pages in a subdirectory with no index.md means the agent won't discover them. Always write an index when batch-offloading.
- **Forgetting to read index**: The meta-entry tells future agents to "read index.md before re-deriving." Future agents must actually do this.
- **ChromaDB drift**: If ChromaDB is down or unreachable, fall back to `search_files` across `claude-vault/03-Knowledge/` instead of failing silently.
- **Over-correction**: Don't offload entries that genuinely need to be in every turn (e.g., "Paperclip API base URL" is short and used constantly — keep in HOT).
