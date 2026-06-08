# Swarm Memory Ideation Framework — 4 Pillars, 8 Proposals

Source: Edgeless swarm ideation session, 2026-05-27

## The North Star
Every agent turn starts with the right context. Every session ends as durable knowledge. Every piece of knowledge finds its connections.

## Pillar 1: Proactive Context Injection

**A. Pre-Flight Knowledge Query**
Before handling a task, auto-query:
- ChromaDB `unified_knowledge` for semantic matches
- Vault for relevant MOC pages and recent reports
- Agent's own MEMORY.md for related past decisions
Inject top-k as `[RELEVANT CONTEXT]` block in system prompt.

**B. Swarm Context Broker**
A lightweight Chroma collection (`swarm_working_memory`) acting as shared scratchpad:
- Schema: `agent, timestamp, content, tags, importance, related_tasks`
- Every turn: read matching tags, write key decisions
- Auto-scored importance via LLM

## Pillar 2: Session-to-Knowledge Extraction

**C. Automatic Session Digest**
After every session, extract:
1. Key Decisions (immutable facts)
2. New Learnings (patterns, gotchas)
3. Problems & Solutions
4. Skill Gaps (what should be a skill?)
5. Cross-References

Output: YAML frontmatter + markdown → `04-Sessions/digests/<id>.md` + ChromaDB upsert.

**D. The Learning Loop**
Weekly cron:
1. Read all session digests
2. Identify recurring patterns (>2 mentions = signal)
3. Propose skill updates/new skills
4. Generate "What Edgeless Learned This Week" report
5. Auto-create Paperclip issues for skill maintenance

## Pillar 3: Cross-Agent Memory Reconciliation

**E. Memory Merge Protocol**
Post-mission:
1. Collect per-agent MEMORY.md changes
2. Deduplicate and rank
3. Write shared insights to `swarm_working_memory`
4. Write canonical long-form to vault `03-Knowledge/Swarm-Learning/`
5. Update each agent's MEMORY.md with cross-references (not full text)

**F. Codex/Claude Code Context Extraction**
Parse session transcripts (`.claude/sessions/`), extract patterns/errors/solutions, write to ChromaDB `code_patterns` track, update skills.

## Pillar 4: Knowledge Health System

**G. Knowledge Vitality Dashboard**
Weekly report tracking:
- Ingestion velocity (notes/day)
- Enrichment coverage (% with key_insights, vault_connections)
- Cross-reference density (avg links per note)
- Query utility (ChromaDB useful return rate)
- Agent memory utilization (query frequency)

**H. Connection Miner**
Nightly cron samples random note pairs from ChromaDB, finds high-similarity pairs with no explicit links, proposes `vault_connections`, surfaces "surprising connections" across domains.

## Implementation Sequence

| Phase | What | ETA |
|-------|------|-----|
| 0 | Fix `chroma_vault_sync_pipeline.py` crash on empty runs | 1h |
| 1 | Create `swarm_working_memory` Chroma collection + schema | 2h |
| 2 | Build pre-flight knowledge query | 4h |
| 3 | Session digest extraction agent + learning loop | 8h |
| 4 | Memory merge protocol | 4h |
| 5 | Codex/Claude Code transcript parser | 6h |
| 6 | Knowledge vitality dashboard + connection miner | 6h |
