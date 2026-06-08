# Overnight Blog Topic Miner

Autonomous agent that mines cross-domain blog topic frameworks from a ChromaDB knowledge vault. Runs as an overnight goal loop (max 5 cycles) with cross-pollination between semantic domains.

## How It Works

1. **Discover collections** — Query ChromaDB v2 API for active collections with document counts
2. **Pick domain pair** — Randomly select two collections from different domain groups (learning, systems, money, agents, ops)
3. **Sample documents** — Pull 4 random docs from each collection + bridge docs via `where_document` keyword overlap
4. **Find the bridge** — Prompt LLM to find the most surprising conceptual connection between the two domains
5. **Emit framework** — Write structured markdown with TITLE / THESIS / HOOK / 5 SECTIONS / SOURCES / ANGLE / CONFIDENCE
6. **Log & iterate** — JSONL event log for observability; abort only after 3 consecutive empty cycles

## Domain Groupings

| Domain | Collections |
|--------|-------------|
| learning | youtube_transcripts, youtube_summaries, unified_knowledge |
| systems | knowledge_spine, skills_system, moip_patterns |
| money | money_lab_insights, trading_knowledge |
| agents | persona_vectors, hermes_learnings, agent-patterns |
| ops | email_triage, social_media, research |

## Output Schema

```yaml
---
title: "The Blog Title"
type: blog-framework
cycle: 1
domains: [money, agents]
created: 2026-05-21
confidence: high
content_hash: abc123
status: draft
---

# Title

> **Thesis:** One-sentence argument.

## Hook
Opening paragraph concept.

## Raw Outline
Full structured output from the LLM.
```

## Key Design Decisions

- **Frameworks only, not full blogs** — The miner stops at structured outlines. Full posts are written in Stage 2 (Drafts) by a writer agent.
- **Cross-domain bridge** — The most interesting topics live at the intersection of two knowledge areas, not within one.
- **Confidence scoring** — LLM self-assesses connection strength. Low-confidence frameworks can still be drafted but are flagged.
- **Content-hash deduplication** — Same framework won't be written twice even if the miner reruns.
- **Fallback on LLM failure** — If the model fails or returns NO_CONNECTION, a simple fallback framework is written so the pipeline keeps moving.

## ChromaDB v2 API Notes

See `references/chromadb-v2-api-patterns.md` for control-character stripping, count endpoint quirks, and sampling patterns.

## Canonical Location

Script: `~/claude-projects/scripts/overnight_blog_topic_miner.py`
Output: `claude-vault/07-Business/Blog-Pipeline/01-Frameworks/`
Log: `claude-vault/07-Business/Blog-Topics/.miner-log.jsonl`
