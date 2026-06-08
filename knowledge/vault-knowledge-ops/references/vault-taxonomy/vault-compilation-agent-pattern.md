# Vault Compilation Agent Pattern

**Session**: 2026-05-12 (Task 334 eval)  
**Agent**: Kimi K2.6 (Hive)  
**Domain**: Automated vault synthesis from ChromaDB + markdown cross-reference

## Problem

Vault notes are write-once with no auto-synthesis. 7,000+ files and 17K ChromaDB embeddings accumulate without cross-referencing, contradiction detection, or browsable MOC generation. Same topics scatter across `fxhash/`, `fxhash-on-chain/`, `OnChain-Art/`, `OnChainGenerativeArt/` — four folders for one concept.

## Solution

Scheduled Python agent that:
1. Queries ChromaDB collections by domain
2. Scans vault markdown for matching keywords
3. Detects contradictions (duplicate folders, stale wiki links)
4. Generates a MOC (Map of Content) markdown page per domain
5. Writes idempotently via content-hash deduplication

## Architecture

```
ChromaDB (20 collections, 17K embeddings)
        │
        ▲  query by domain keywords
        │
VaultCompilationAgent
        │
    ┌──┘┘──┐
    ▲         ▲
Vault     Chroma docs
files     (metadata + content preview)
    │         │
    └────────┘
         │
    [Contradiction Detection]
    - Duplicate folders: normalize names, flag collisions
    - Stale refs: parse [[wiki links]], verify target exists
         │
    [MOC Generation]
    - YAML frontmatter with metrics
    - Vault source list with bidirectional links
    - Chroma source list with collection attribution
    - Contradictions section with actionable suggestions
         │
    [Idempotent Write]
    - Compute content hash (domain + all_text[:500])
    - Compare to hash embedded in existing file
    - Skip if match, overwrite if drift
```

## Key Implementation Details

### Domain Configuration
```python
SYNTHESIS_DOMAINS = [
    "multi-agent-patterns",
    "creative-tooling",
    "trading-infrastructure",
]

DOMAIN_COLLECTION_MAP = {
    "multi-agent-patterns": ["agent-patterns", "project_knowledge", "knowledge_spine"],
    "creative-tooling": ["knowledge", "research", "skills_system"],
    "trading-infrastructure": ["trading_knowledge", "money_lab_insights"],
}
```

### Contradiction Detection

**Duplicate folders**: Strip punctuation and case, compare normalized keys.
```python
key = re.sub(r"[^a-z0-9]+", "", name.lower())
# 'OnChain-Art' → 'onchainart'
# 'On-Chain-Art' → 'onchainart'  → COLLISION
```

**Stale wiki links**: Parse `[[Link Target]]`, check if any candidate path exists:
```python
candidates = [
    link_clean + ".md",
    link_slug + ".md",
    link_clean,
    link_slug,
]
```

### Idempotency Mechanism

Embed hash in file footer:
```markdown
*Last compiled by vault-compilation-agent. Hash: a864d05efc51e881*
```

Recompute on every run:
```python
all_text = " ".join(d.get("content", "") for d in chroma_docs + vault_files)
new_hash = fingerprint(domain + all_text[:500])
```

**Critical**: Generation and verification must use the **exact same** `all_text` construction. A mismatch in join order or truncation causes false-positive rewrites.

### Safety Defaults
```bash
DRY_RUN=1   # Preview only — default
APPLY=1     # Actually write — explicit opt-in
```

## Results from Production Run (2026-05-12)

| Domain | Vault Files | Chroma Docs | Contradictions | Output Size |
|--------|-------------|-------------|----------------|-------------|
| Multi-Agent Patterns | 41 | 24 | 2 (duplicate folders) | 6,778 B |
| Creative Tooling | 64 | 33 | 46 (44 stale + 2 dupes) | 11,880 B |
| Trading Infrastructure | 12 | 48 | 41 (39 stale + 2 dupes) | 9,068 B |

**Notable findings**:
- `MOCs` vs `_MOCs` — duplicate folder (normalized: `mocs`)
- `OnChain-Art` vs `On-Chain-Art` vs `OnChainGenerativeArt` — 3 variants
- 83 stale wiki links across domains pointing to non-existent files

## Cron Integration

```bash
# Weekly audit (dry run)
0 3 * * 0 cd ~/claude-projects && DRY_RUN=1 python scripts/vault-compilation-agent.py

# Monthly apply
0 3 1-7 * 0 cd ~/claude-projects && APPLY=1 python scripts/vault-compilation-agent.py
```

## Extending the Agent

To add a new domain:
1. Add domain string to `SYNTHESIS_DOMAINS`
2. Map to ChromaDB collections in `DOMAIN_COLLECTION_MAP`
3. Add vault scan keywords in `scan_vault_for_domain()`
4. Re-run with `DRY_RUN=1` to preview

## Related

- `../SKILL.md` — Taxonomy enforcement and migration workflow
- `../references/collision-remediation-session-2026-05-05.md` — Manual remediation session
- `~/claude-projects/scripts/vault-compilation-agent.py` — Production implementation
