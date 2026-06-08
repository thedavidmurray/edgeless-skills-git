# Source-to-Derivatives Pipeline: One URL → Vault + ChromaDB + Creative + Social

**Session:** 2026-05-21 | **Source:** Gutenberg eBook #49 (Polly, 1992) | **Agent:** Hive

## When to Use

User drops a URL and asks for simultaneous:
- Ingestion into knowledge spine (vault + ChromaDB)
- Creative artifact generation (Hermes-native comic, image, diagram)
- Social content drafting (evergreen tweet bank, thread skeleton)

**Do NOT use** for simple "summarize this URL" requests — that is single-track. This pipeline activates only when the user explicitly asks for multiple output types or says things like "also make X" / "and draft Y" alongside ingestion.

## Workflow

### Phase 1: Source Fetch (Parallelizable)

```
web_extract(url) → browser_navigate + scroll if needed → full text capture
```

**Pitfall:** web_extract sometimes truncates. If content >5K chars, follow up with browser tools to scroll and capture remaining sections. Combine outputs before analysis.

### Phase 2: Analysis → Three Parallel Tracks

| Track | Tool | Output Spec | Canonical Path |
|-------|------|------------|----------------|
| **Knowledge** | write_file | Markdown with YAML frontmatter, KB score 12+, structured sections (Executive Summary, Key Insights w/tables, Technical Context, Cultural Impact, Timeline, Action Items) | `claude-vault/03-Knowledge/<topic>/` |
| **ChromaDB** | chromadb.HttpClient | Semantic embedding with metadata (source, author, year, topic, vault_path, title) | `knowledge_spine` collection |
| **Creative** | image_generate | Hermes-native artifact matching user's aesthetic (retro-futuristic / terminal-brutalist / ligne-claire per baoyu-comic-pipeline skill) | Inline URL delivery |
| **Social** | write_file | Evergreen tweet bank: 12+ tweets, all <280 chars, copy-paste ready, with usage notes (tone, timing, thread pairing) | `claude-vault/07-Business/Social-Media/` |

**Critical:** Run knowledge + social writes in parallel with creative generation. Do NOT sequence them. The user expects all outputs from one pass.

### Phase 3: Verification

| Claim | Verification |
|-------|-------------|
| Vault file written | `ls -la <path>` |
| ChromaDB embedded | `collection.count()` before/after comparison |
| Image generated | URL returned from image_generate |
| Tweet bank written | `ls -la <path>` |

### Phase 4: Consolidated Report

Present all three tracks in a single summary block:
1. Knowledge spine path + ChromaDB collection + doc count delta
2. Creative artifact URL (rendered inline as markdown image)
3. Tweet bank path + tweet count + sample hook

Do NOT send three separate messages. One message, three sections, clear headers.

## Deliverable Specifications

### Knowledge Article Spec

```yaml
---
title: "<Title> — <Author>, <Year>"
source: "<Domain or publication>"
url: "<Original URL>"
author: "<Name>"
published: "<Date>"
triage_score: <1-10>
topics: [<list>]
kb_score: <12-15 target>
status: enriched
tracks: [knowledge, creative_seeds]
vault_connections: [[Related-1]], [[Related-2]]
---
```

**Required sections:** Executive Summary (4-6 sentences), Key Insights (numbered, with tables for data), Technical Context, Cultural Impact & Legacy, Timeline, Action Items (checkbox list), Source Document block.

### ChromaDB Embedding Spec

```python
collection.add(
    ids=["<slugified-title>"],
    documents=["<200-400 word condensed summary>"],
    metadatas=[{
        "source": "<domain>",
        "author": "<name>",
        "year": <int>,
        "topic": "<primary-topic>",
        "vault_path": "<relative-path>",
        "title": "<title>"
    }]
)
```

**Pitfall:** ChromaDB v2 REST API is unstable. Fall back to `chromadb.HttpClient` Python client if REST returns 404/422/"Unimplemented".

### Tweet Bank Spec

```yaml
---
title: "Evergreen Tweet Bank — <Topic>"
source: "<vault-source-file>"
status: draft
purpose: "Ready-to-post bangers on <topic>"
tweet_count: <N>
tone: "educational-banger — facts that hit"
---
```

**Each tweet must include:**
- T-numbered ID (T1, T2...)
- Full copy-paste text block
- Character count (verified <280)
- Best-for timing note
- Hook explanation (why it works)
- Thread pairing suggestion

**Usage notes section:** Table with columns Tweet, Tone, Timing, Thread Pairing.

### Creative Artifact Spec

- Must match user's aesthetic preference from user profile (retro-futuristic / terminal-brutalist / CRT-phosphor for non-comic; ligne-claire for comics per baoyu-comic-pipeline)
- Must be "Hermes-native" — generated via agent tools, not outsourced
- Comic panels: use baoyu-comic-pipeline SKILL.md character bible and anti-human guardrails
- Always include caption/context with artifact so user understands what they're seeing

## ChromaDB Fallback Pattern

When REST API v2 fails with "Unimplemented" or 404/422:

```python
import chromadb
client = chromadb.HttpClient(host="localhost", port=8100)
collection = client.get_collection("knowledge_spine")
collection.add(ids=[...], documents=[...], metadatas=[...])
```

This is the reliable path. The REST API shifts between v1 and v2 across ChromaDB versions. The Python client auto-negotiates.

## Parallel Execution Template

```python
# In practice, use execute_code or terminal for the ChromaDB fallback,
# image_generate for creative, write_file for knowledge + social.
# All three can fire simultaneously once source text is captured.

# Example from Polly 1992 session:
# 1. web_extract(url) → content
# 2. Parallel:
#    a. write_file(vault_path, knowledge_md)
#    b. image_generate(prompt=creative_prompt)
#    c. write_file(social_path, tweet_bank_md)
# 3. After creative returns, ChromaDB add via Python client
# 4. Verify all four claims
# 5. Single consolidated report
```

## Related Skills

- `baoyu-comic-pipeline` — ligne-claire comic generation, character bibles, anti-human guardrails
- `vault-knowledge-ops` (this skill) — taxonomy enforcement, enrichment schema, 3-tier memory
- `scraping-intel` — if source requires deeper extraction than web_extract provides

## Canonical Output Paths

| Track | Path |
|-------|------|
| Knowledge | `~/claude-projects/claude-vault/03-Knowledge/<topic>/<Slugified-Title>.md` |
| Social | `~/claude-projects/claude-vault/07-Business/Social-Media/Evergreen-Tweets-<Topic>.md` |
| ChromaDB | `knowledge_spine` collection |
| Creative | Inline URL (delivered in report) — no local file needed unless user requests |
