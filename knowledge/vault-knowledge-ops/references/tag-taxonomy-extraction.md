---
title: Tag Taxonomy Extraction from Vault
created: 2026-05-21
updated: 2026-05-21
type: reference
tags: [vault, taxonomy, tags, frontmatter, knowledge-management]
---

# Tag Taxonomy Extraction from Vault

> Session 2026-05-21: Extracted ~80 raw tags from 200 vault notes, consolidated to 30 canonical tags with 18 deprecated aliases.

## When to Use

- Tag sprawl detected across vault (duplicate meaning, different spellings, overlapping concepts)
- New frontmatter schema needs a canonical tag list
- Vault quality audit identifies orphan or inconsistent tags
- Preparing for wiki-lint or automated classification

## Extraction Technique

### Step 1: Harvest Raw Tags

```bash
# From all .md files with frontmatter in 03-Knowledge/
grep -rh "^tags:" ~/claude-projects/claude-vault/03-Knowledge/ 2>/dev/null | \
  sed 's/tags: //;s/\[//;s/\]//;s/"//g' | \
  tr ',' '\n' | tr -d ' ' | sort | uniq -c | sort -rn
```

For large vaults (5,000+ files), sample instead of scanning all:
```bash
find ~/claude-projects/claude-vault/03-Knowledge -name "*.md" -maxdepth 3 | \
  shuf | head -200 | while read f; do
    grep -m1 "^tags:" "$f" 2>/dev/null | sed 's/tags: //;s/\[//;s/\]//;s/"//g;s/, /\n/g'
done | sort | uniq -c | sort -rn | head -80
```

### Step 2: Consolidate to Canonical Tags

Group raw tags by semantic similarity. Typical consolidation pattern:

| Canonical Tag | Deprecated Aliases (map these) |
|---------------|-------------------------------|
| `agent-infrastructure` | agents, swarm, discord-bots, bot-deployment |
| `knowledge-management` | vault, wiki, knowledge-base, kb |
| `trading` | polymarket, market-analysis, trading-strategy |
| `design-system` | design, ui, tokens, visual-design |
| `content-enrichment` | enrichment, triage, rss, youtube |
| `paperclip` | paperclip-api, backlog, issue-management |

Rules:
- Prefer hyphenated lowercase (kebab-case)
- Prefer domain-concept over tool-name (e.g., `trading` > `polymarket`)
- Prefer 2-word compound over abbreviation (e.g., `knowledge-management` > `km`)
- Group tool-specific tags under broader domain unless the tool IS the domain (e.g., `paperclip` stays because it's both tool and system)

### Step 3: Write Canonical Taxonomy

Write to `10-Meta/tag-taxonomy.md` with three sections:

1. **Canonical Tags** — the 20-30 approved tags with descriptions
2. **Deprecated Aliases** — old tags that should be replaced
3. **Consolidation Rules** — heuristics for future tag decisions

### Step 4: Wire Into Frontmatter Schema

Patch `_system/FRONTMATTER-SCHEMA.md` to reference the canonical list:

```yaml
tags: [tag1, tag2]  # MUST use canonical tags from 10-Meta/tag-taxonomy.md
```

Do NOT auto-rename tags in existing notes during initial creation — that creates a mass-edit churn. Instead, add deprecated aliases to the taxonomy so future enrichment uses canonical tags, and existing notes get updated opportunistically during normal edits.

## Verification

After writing the taxonomy, verify coverage:

```bash
canonical_count=$(grep -rlh "tags:.*\bagent-infrastructure\b" ~/claude-projects/claude-vault/03-Knowledge/ 2>/dev/null | wc -l)
alias_count=$(grep -rlh "tags:.*\bagents\b" ~/claude-projects/claude-vault/03-Knowledge/ 2>/dev/null | wc -l)
echo "Canonical: $canonical_count, Alias: $alias_count"
```

## Pitfalls

- **Don't scan the whole 19K-file vault** — it's mostly session logs and raw ingests without frontmatter. Sample 200-500 curated notes from `03-Knowledge/` instead.
- **Don't auto-backfill** — mass tag renaming creates churn and conflicts with concurrent edits. Let canonical tags accumulate organically.
- **Don't require tags on all notes** — raw captures and session logs don't need frontmatter at all. Apply taxonomy only to curated knowledge notes.
- **Tool-vs-domain ambiguity** — `paperclip` is both a tool and the system name, so it stays. `notebooklm` is a tool, so it maps to `knowledge-management` or `content-enrichment`.
