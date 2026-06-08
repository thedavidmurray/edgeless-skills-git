---
title: Vault Wiki Integration Pattern
created: 2026-05-21
updated: 2026-05-21
type: reference
tags: [vault, wiki, obsidian, integration, llm-wiki, knowledge-management]
---

# Vault Wiki Integration Pattern

> Session 2026-05-21: Merged llm-wiki skill with existing Obsidian vault infrastructure.
> Key lesson: bridge existing wiki, don't rebuild it.

## What Exists (Do Not Recreate)

The vault already has a working wiki at `03-Knowledge/wiki/` with:
- `master_index.md` — canonical entry point (not `index.md`)
- `raw/` — staging area (empty as of 2026-05-21)
- `published/` — curated topics (`Karpathy-KB-Pattern/` seeded by Scribe)
- `CLAUDE.md` — wiki-specific schema rules (filesystem-native, no vectors)

The vault also has:
- `03-Knowledge/MOCs/` — 27 Obsidian-native Maps of Content (AI-Agents.md, Discord.md, etc.)
- `_system/TAXONOMY.md` — canonical folder structure v3
- `_system/FRONTMATTER-SCHEMA.md` — split schema (`note_type` + `content_type`) v2.0
- `10-Meta/tag-taxonomy.md` — canonical tag list (30 tags from ~80 raw)
- `10-Meta/wiki-log.md` — action log for wiki operations
- `10-Meta/wiki-lint-report.md` — lint findings

## The Bridge Architecture

```
claude-vault/                    ← WIKI_PATH (vault-as-wiki root)
├── 00-Inbox/                    ← Layer 1: Raw (immutable after capture)
├── Clippings/                   ← Layer 1: Raw (Obsidian Web Clipper)
├── 04-Sessions/                 ← Layer 1: Raw (session logs, read-only)
├── 03-Knowledge/                ← Layer 2: The Wiki (curated, cross-linked)
│   ├── wiki/                    ← Karpathy-style filesystem wiki
│   │   ├── master_index.md      ← References ALL knowledge areas
│   │   ├── raw/                 ← Staging (promote to published/)
│   │   ├── published/           ← Curated topics with index.md per topic
│   │   └── CLAUDE.md            ← Wiki schema (no vectors rule)
│   ├── MOCs/                    ← 27 Obsidian-native index pages
│   ├── RSS/                     ← Curated articles (50+)
│   ├── YouTube/                 ← Video transcripts, clusters (100+)
│   ├── Articles/                ← Curated web articles (30+)
│   ├── Agent-Infrastructure/      ← Agent patterns, incidents (9+)
│   └── ... (25 more areas)      ← Domain-specific knowledge collections
├── 14-Knowledge-Bases/          ← Layer 2: Compiled KBs (NotebookLM-ready)
├── 15-Products/                 ← Layer 2: Product documentation
├── 16-Projects/                 ← Layer 2: Project memory
├── 02-Agents/                   ← Layer 2: Agent personas, configurations
├── 05-Solutions/                ← Layer 2: Problem-solution pairs
├── 08-Reference/                ← Layer 2: External reference docs
├── 13-Reports/                  ← Layer 2: Generated reports, audits
├── 10-Meta/                     ← Layer 3: Schema, logs, lint reports
│   ├── wiki-log.md              ← Chronological action log (append-only)
│   ├── wiki-lint-report.md      ← Latest lint findings
│   ├── tag-taxonomy.md          ← Canonical tag list
│   └── CLAUDE.md                ← Vault master config
└── _system/                     ← Layer 3: Templates, schema definitions
    ├── TAXONOMY.md                ← Folder structure v3
    ├── FRONTMATTER-SCHEMA.md      ← YAML rules (v2.0 split schema)
    └── templates/                 ← Note templates, prompt templates
```

## Integration Rules

### 1. Start at `master_index.md`, Not `SCHEMA.md`

The wiki skill says "Read SCHEMA.md first" — but the vault's schema is in `_system/FRONTMATTER-SCHEMA.md`, not a wiki-specific `SCHEMA.md`. For vault integration:

1. Read `03-Knowledge/wiki/master_index.md` — lists wiki topics + vault knowledge areas
2. Read `03-Knowledge/wiki/CLAUDE.md` — wiki-specific rules (no vectors, filesystem-native)
3. Read `_system/FRONTMATTER-SCHEMA.md` — vault-wide YAML conventions
4. Read `10-Meta/tag-taxonomy.md` — canonical tags
5. Read `10-Meta/wiki-log.md` — recent activity

### 2. Use MOCs as the Index Layer

The vault has 27 MOCs in `03-Knowledge/MOCs/`. These are Obsidian-native and superior to flat `index.md` for navigation. When querying:
- Read relevant MOCs for domain overview
- Follow `[[wikilinks]]` from MOCs to specific notes
- Cross-reference with `master_index.md` for wiki-curated topics

### 3. Frontmatter Convergence

The vault uses a **split schema** (`note_type` + `content_type` + `status` + `created`/`updated` + `tags`).

Safe additions that don't conflict:
- `confidence: high|medium|low` — quality signal
- `contested: true` — flags unresolved contradictions

Fields to avoid (already covered by existing schema):
- `type: entity|concept|comparison|query` — conflicts with `note_type`
- `contradictions: [page-slug]` — too much bookkeeping, use `related:` wikilinks
- `sources: [raw/file.md]` — use `source_url` or `related:` instead

### 4. Raw Layer Already Exists

- `00-Inbox/` — RSS ingests, YouTube summaries, raw notes
- `Clippings/` — Web Clipper captures (browser extension)
- `04-Sessions/` — Session logs (auto-generated)

Do NOT create a separate `wiki/raw/` for vault content — use the existing raw layers. The `wiki/raw/` is only for wiki-specific staging.

### 5. Action Log and Lint Reports Go in `10-Meta/`

- `10-Meta/wiki-log.md` — chronological record of wiki actions
- `10-Meta/wiki-lint-report.md` — regenerated on each lint
- NOT in `wiki/` root — the vault's meta layer is `10-Meta/`

## Anti-Patterns (Session-Learned)

| Anti-Pattern | What Happened | Correct Approach |
|--------------|---------------|------------------|
| Propose `SCHEMA.md` + `index.md` + `log.md` in wiki root | Vault already had `_system/TAXONOMY.md`, `_system/FRONTMATTER-SCHEMA.md`, `MOCs/`, `10-Meta/wiki-log.md` | Extend `master_index.md` and `FRONTMATTER-SCHEMA.md` instead |
| Propose `entities/` + `concepts/` subdirs | Vault already has 25+ domain folders in `03-Knowledge/` | Keep domain folders as organizational axis |
| Propose SHA256 source drift detection | Triage pipelines already deduplicate via `sha256` in `raw/` | Skip — solution looking for a problem |
| Propose new `_system/scripts/wiki-lint.py` | Wiki skill already has `wiki-lint` built in | Use existing `wiki-lint` skill command |
| Ignore existing `master_index.md` | Only listed 1 wiki topic when 27 knowledge areas exist | Extended to reference all knowledge areas with descriptions |

## Quick Start for Future Sessions

```bash
# 1. Detect existing wiki
ls ~/claude-projects/claude-vault/03-Knowledge/wiki/
# Expected: master_index.md, raw/, published/, CLAUDE.md

# 2. Read the wiki entry point
read_file ~/claude-projects/claude-vault/03-Knowledge/wiki/master_index.md

# 3. Read the vault schema
read_file ~/claude-projects/claude-vault/_system/FRONTMATTER-SCHEMA.md
read_file ~/claude-projects/claude-vault/10-Meta/tag-taxonomy.md

# 4. Query a topic via MOCs
read_file ~/claude-projects/claude-vault/03-Knowledge/MOCs/<Topic>.md

# 5. Search for specific content
search_files "keyword" path="~/claude-projects/claude-vault/03-Knowledge" file_glob="*.md"
```

## Related References

- `references/agent-memory/3-tier-offload-pattern.md` — MEMORY.md overflow management
- `_system/TAXONOMY.md` — Vault folder structure v3
- `_system/FRONTMATTER-SCHEMA.md` — YAML frontmatter rules v2.0
- `03-Knowledge/wiki/CLAUDE.md` — Wiki-specific schema (filesystem-native, no vectors)
