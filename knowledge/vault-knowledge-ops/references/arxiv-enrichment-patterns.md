# arXiv Enrichment Patterns

Reusable patterns for upgrading minimal RSS-pipeline arXiv notes into full KB articles.

## arXiv API (Metadata)

The export.arxiv.org API returns XML Atom feed format. Use grep/sed one-liners to extract fields without parsing XML:

```bash
ID="2605.27681"
BASE="https://export.arxiv.org/api/query?id_list="

# Abstract
curl -s "${BASE}${ID}" | grep -o '<summary>[^<]*' | sed 's/<summary>//'

# Authors (one per line)
curl -s "${BASE}${ID}" | grep -o '<name>[^<]*' | sed 's/<name>//'

# Published date
curl -s "${BASE}${ID}" | grep -o '<published>[^<]*' | sed 's/<published>//'

# Categories (one per line)
curl -s "${BASE}${ID}" | grep -o '<category term="[^"]*' | sed 's/<category term="//'

# Title
curl -s "${BASE}${ID}" | grep -o '<title>[^<]*' | sed 's/<title>//;s/^[[:space:]]*//'
```

**Pitfall:** Do NOT use `http://export.arxiv.org` — the security scanner blocks plain HTTP. Always use `https://`.

## Jina AI Reader (Full Page Extraction)

When the arXiv abstract is insufficient and the paper's HTML page or blog post contains more context:

```bash
# Any URL — returns clean markdown
curl -s "https://r.jina.ai/http://arxiv.org/abs/2605.27681" | head -100

# Or the full page
curl -s "https://r.jina.ai/http://www.lesswrong.com/posts/SLUG/title"
```

**Limitations:** Jina may return 429 (rate limit) or Vercel security checkpoints on some domains. Fallback to the arXiv API for reliable metadata.

## Two-Stage Enrichment Flow

### Stage 1: RSS Pipeline Output (Minimal)

```markdown
# Reasoning and Planning with Dynamically Changing Norms

**Score:** 10/10
**Source:** cs.AI
**Link:** https://arxiv.org/abs/2605.27622
**Published:** Thu, 28 May 2026 00:00:00 -0400

arXiv:2605.27622v1 Announce Type: new
Abstract: To safely interact with humans...
```

### Stage 2: Enriched KB Article (Full)

```yaml
---
title: "Behavioural Analysis of Alignment Faking"
source: "arXiv"
url: "https://arxiv.org/abs/2605.27681"
published: "2026-05-26"
triage_score: 9.6
kb_score: 13
status: enriched
topics:
  - ai-alignment
  - alignment-faking
  - mechanistic-interpretability
  - ai-safety
  - sycophancy
  - activation-steering
context: >
  Foundational research decomposing alignment faking (AF) into three separable
  drivers...
one_liner: >
  Alignment faking is not a monolithic failure mode; it decomposes into three
  independently measurable drivers...
enrichment_tier: Tier-3
vault_connections:
  - "[[AI Alignment Knowledge Base]]"
  - "[[Mechanistic Interpretability Index]]"
---
```

**Required sections for kb_score 12+:**
1. Executive summary (2-3 bullets)
2. Technical deep-dive (tables, drivers, experimental design)
3. Comparison with prior work (table)
4. Real-world applications (safety, RLHF, interpretability)
5. Action items checklist
6. Key quotes (2-3 blockquotes)
7. Cross-references (wikilinks to existing vault notes)
8. Changelog

## Paperclip Checkout (Claiming the Issue)

```bash
# WRONG — 'open' is not a valid enum
curl -s -X POST http://127.0.0.1:3100/api/issues/EDGA-6025/checkout \
  -H "Content-Type: application/json" \
  -d '{"agentId":"...","expectedStatuses":["open"]}'
# → {"error":"Validation error","details":[{"code":"invalid_enum_value"...}]}

# CORRECT — use the actual status of the ticket (usually 'todo' or 'backlog')
curl -s -X POST http://127.0.0.1:3100/api/issues/EDGA-6025/checkout \
  -H "Content-Type: application/json" \
  -d '{"agentId":"...","expectedStatuses":["todo"]}'
```

Valid `expectedStatuses` values: `backlog`, `todo`, `in_progress`, `in_review`, `done`, `blocked`, `cancelled`.

## Verification

After writing the KB article:

```bash
# Confirm file exists and has frontmatter
head -n 20 ~/claude-projects/claude-vault/03-Knowledge/RSS/cs.AI/behavioural-analysis-of-alignment-faking.md

# Check kb_score is present
grep "kb_score:" ~/claude-projects/claude-vault/03-Knowledge/RSS/cs.AI/behavioural-analysis-of-alignment-faking.md

# Post completion comment to Paperclip
curl -s -X POST http://127.0.0.1:3100/api/issues/EDGA-6025/comments \
  -H "Content-Type: application/json" \
  -d '{"body":"KB article enriched and written to vault: ..."}'
```

## PDF Direct Extraction (User-Initiated)

When the user directly shares an arXiv PDF URL (e.g., `https://arxiv.org/pdf/2605.26379`) rather than going through the RSS pipeline, `web_extract` will truncate at ~5K chars because PDFs are 6-8MB. Use the following fallback chain:

### Step 1: Try web_extract (will likely truncate)
```python
web_extract(urls=["https://arxiv.org/pdf/2605.26379"])
# Returns truncated content with hint: "[Content truncated — showing first 5,000 of 165,643 chars]"
```

### Step 2: Download PDF via curl
```bash
curl -sL -o /tmp/arxiv_{id}.pdf https://arxiv.org/pdf/{id}
# Verify: ls -lh /tmp/arxiv_{id}.pdf  (expects 6-8MB)
```

### Step 3: Extract text via pdftotext
```bash
# Check availability first
which pdftotext || brew install poppler  # macOS

# Extract with layout preservation
pdftotext -layout /tmp/arxiv_{id}.pdf /tmp/arxiv_{id}.txt
# Verify: wc -l /tmp/arxiv_{id}.txt  (expects 2000-3000 lines)
```

### Step 4: Chunked reading
```python
read_file(path="/tmp/arxiv_{id}.txt", offset=1, limit=500)
# Continue in 500-line chunks until all content is read
```

### Step 5: Compose structured vault entry

Write to the appropriate vault path. For user-initiated direct extraction (no RSS pipeline), use `04-Sessions/`:

```
/Users/djm/claude-projects/claude-vault/04-Sessions/arxiv-{id}-{short-title}.md
```

**Structured entry template:**

```yaml
---
title: "Full Paper Title"
authors: "Author1, Author2..."
arxiv: "{id}v1"
date: "YYYY-MM-DD"
category: stat.ML|cs.LG|...
tags: [topic1, topic2, ...]
---

## Summary

1-2 paragraph overview of the paper's core contribution.

---

## 1. Key Theoretical Results

### Result N: Title
**Statement:** [Exact theorem statement or paraphrase]
**Proof mechanism:** [Key insight of the proof]

---

## 3. Experimental Validation

### Section Name (Sec X.Y)
- Key results, tables, comparisons

---

## 4. Limitations & Open Questions

- List from the paper's limitations section

---

## 5. Connection to Prior Work

- How this fits into the broader landscape

---

## Key Insight

The single most important takeaway that makes this paper worth remembering.
```

**Section density:** Preserve theorem-level detail (the user is adding to a knowledge base, not skimming). Include proof mechanisms (Hermite, Sturm-Liouville, etc.), experimental numbers, and the Lean verification status if applicable.

### Pitfalls
- **`web_extract` always truncates arXiv PDFs** — do not retry with different parameters; immediately fall through to curl + pdftotext
- **`pdftotext -layout` vs `pdftotext`** — the `-layout` flag preserves column structure and figure labels; always use it
- **Chunk boundaries** — read in 500-line chunks (the tool's sweet spot); the first chunk is 500 lines but the paper's body starts after ~50 lines of header/aside material
- **Vault path** — for direct user share (not RSS pipeline), write to `04-Sessions/`, not `03-Knowledge/RSS/`
- **Lean verification** — note whether proofs are machine-checked and with how many axiomatized premises
- **Theorems are the anchor** — organize by theorem number, not by "interesting parts" — the user needs to reference Thm. 1, Thm. 2, etc. later
- **Full reference list** — include the paper's own references section so future vault entries can cross-link

## Session Reference

- **EDGA-6025** — 2026-05-28. Full enrichment of "Behavioural Analysis of Alignment Faking" (arXiv:2605.27681). Used all patterns above.
- **LeJEPA World Model (2605.26379)** — 2026-05-29. Direct PDF extraction of Klindt/LeCun/Balestriero paper. Used curl+pdftotext+chunked read. Wrote to `04-Sessions/`.
