# Academic PDF Knowledge Spine Ingestion

Reproducible workflow for ingesting academic textbooks (e.g., SLP3) or research papers into the knowledge vault as structured knowledge spine entries, then deriving actionable tasks and dispatching them to the swarm.

## Overview

This workflow was battle-tested on Jurafsky & Martin's *Speech and Language Processing* (3rd ed., 2026) — 25 chapters + appendices. It produces:
1. A structured knowledge spine markdown entry per chapter
2. Paperclip issues for actionable tasks (one per chapter)
3. Discord swarm dispatch to the appropriate agent

## Workflow

```
1. Download PDF
   ↓ curl -sL "https://web.stanford.edu/~jurafsky/slp3/{N}.pdf" -o /tmp/slp3-ch{N}.pdf

2. Extract text
   ↓ pymupdf (fitz) → /tmp/slp3-ch{N}-text.txt

3. Structure into knowledge spine
   ↓ Read key sections (first 150 lines, offset 400, 1100, etc.)
   ↓ Identify: core concept, key equations, algorithmic steps, Edgeless relevance
   ↓ Write to: claude-vault/03-Knowledge/Knowledge-Spine/{topic}.md

4. Define actionable tasks
   ↓ Identify 3-4 concrete tasks per chapter
   ↓ Each task: ID, scope, deliverables, acceptance criteria, route
   ↓ Do NOT write markdown task files — file directly as Paperclip issues

5. Create Paperclip issue
   ↓ POST to /api/companies/{companyId}/issues
   ↓ Title: "EDGA-CH{N}-001: {brief description}"
   ↓ Priority: P1/P2/P3
   ↓ Labels: [chapter, topic, language, agent]

6. Update master tracker
   ↓ claude-vault/03-Knowledge/Knowledge-Spine/slp3-ingestion-tracker.md
   ↓ Mark chapter ✅ DONE with spine path, issue ID

7. Dispatch to swarm
   ↓ Discord #bot-backroom: [FROM:Hive][TO:{agent}][TYPE:EXECUTE|ENRICH][REF:EDGA-CH{N}]
   ↓ Include task list, issue IDs, ETA

8. Advance to next chapter
   ↓ Repeat from step 1
```

## Knowledge Spine Entry Format

Each chapter produces a markdown file with this structure:

```markdown
# {Chapter Title}

**Source**: {Author}, *{Book}* ({edition}, {date}), Chapter {N}
**URL**: {pdf_url}
**Ingested**: {YYYY-MM-DD}
**Domain**: {topic}
**Agent**: {swarm_agent}

---

## Core Concept

1-paragraph summary of the chapter's central idea.

**Key insight**: The single most important takeaway.

---

## 1. {Section Name}

### {Subsection}
Key equations, algorithms, or definitions.

---

## Edgeless Relevance & Applications

### Immediate Applications
1. {Concrete application}

### Why This Matters for the Swarm
- {Strategic relevance}

### Concrete Swarm Applications
| Task | Architecture | Input | Output | Use Case |
|---|---|---|---|---|

---

## Related Knowledge

- **{Topic}** → [[{linked-file}]] (Chapter {M})

---

## Gaps & Next Steps

- [ ] {Specific gap}

---

**Tags**: #tag1 #tag2 #tag3
```

## Task Definition Template

Each task follows this schema:

| Field | Description |
|---|---|
| **ID** | `EDGA-CH{N}-{NNN}` (e.g., `EDGA-CH3-001`) |
| **Title** | Brief action description |
| **Scope** | What the task covers |
| **Blast radius** | Low / Medium / High |
| **ETA** | Hours estimate |
| **Deliverables** | Bulleted list of concrete outputs |
| **Acceptance criteria** | Measurable success conditions |
| **Route** | `[TO:{agent}][TYPE:EXECUTE|ENRICH|ARCH]` |

## Priority Matrix

| Task | Priority | Effort | Value | Blocked by | Assignee |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

## Tracker Format

The master tracker is a markdown table:

```markdown
| # | Title | Status | Spine Path | Tasks | Paperclip Issue |
|---|---|---|---|---|---|
| **{N}** | {Title} | ✅ DONE | `{spine_path}` | {N} tasks | `{issue_id}` |
| **{M}** | {Title} | 🔄 IN PROGRESS | | | |
```

## Key Technical Details

### Text Extraction
- **Tool**: `pymupdf` (fitz) via Python
- **Method**: `fitz.open(pdf)` then `page.get_text()` per page
### Reading strategy
- Read in chunks of 100-150 lines at strategic offsets:
  - `offset=1` (limit=80): Title, chapter overview, first section
  - `offset=400` (limit=100): Mid-chapter sections, key algorithms
  - `offset=800` (limit=100): Later sections, evaluation, applications
  - `offset=1200` (limit=100): End sections, historical notes, references
- For 22-30 page chapters: 4-5 reads of 100-150 lines each captures full structure
- For 30+ page chapters (e.g., Ch 23, 34 pages, 110K chars): May need 6-7 reads; watch tool limit
- Always note: `total_lines` and `file_size` from the first read_file to plan remaining reads

### PDF Download
- **Command**: `curl -sL "{url}" -o /tmp/{filename}.pdf`
- **Verify**: `ls -lh /tmp/{filename}.pdf` (expect 1-2MB)
- **Timeout**: 30s for download

### Section Discovery
- **Method**: Regex search for chapter section headers: `\n{N}.\d+(?:\.\d+)?\s+([A-Z][A-Za-z\s\-:]+)\n`
- **Keyword scan**: Check for key concepts (e.g., `neural network`, `backpropagation`, `dropout`) to verify coverage

## Paperclip API Pattern

```bash
# Create issue
curl -s -X POST "http://127.0.0.1:3100/api/companies/{companyId}/issues" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "EDGA-CH{N}-001: {description}",
    "description": "{full description with deliverables and acceptance criteria}",
    "priority": "medium",
    "status": "todo",
    "labels": ["topic", "language", "agent"]
  }'

# Extract ID from response
python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('id', '?'))"
```

## Discord Dispatch Format

```
[FROM:Hive][TO:{agent}][TYPE:EXECUTE][REF:EDGA-CH{N}]
{task list with issue IDs}
ETA: {X} hours total. Claim when ready. 🔥
```

## Batch Groupings

For large textbooks, group chapters into batches:

| Batch | Chapters | Theme |
|---|---|---|
| **Foundations** | 2–6 | Tokenization, n-grams, classification, embeddings, neural nets |
| **Modern LLMs** | 7–9 | LLMs, transformers, post-training/alignment |
| **Applied NLP** | 10–16 | MLMs, RAG, MT, RNNs, speech |
| **Linguistic Structure** | 17–25 | Parsing, IE, semantics, discourse, dialogue |
| **Algorithms** | Appendices | HMMs, Naive Bayes, smoothing, spelling, grammars |

## Canonical Locations

| Artifact | Path |
|---|---|
| Knowledge spine entries | `claude-vault/03-Knowledge/Knowledge-Spine/` |
| Master tracker | `claude-vault/03-Knowledge/Knowledge-Spine/slp3-ingestion-tracker.md` |
| Session logs | `claude-vault/04-Sessions/` |
| Reports | `claude-vault/13-Reports/` |

**NEVER write to `Codex-vault/`** — it is a deprecated duplicate.

## Pitfalls

- **`execute_code` may be blocked for long PDF extraction**: On large PDFs (>500KB), `execute_code` can timeout or be blocked. Use `terminal` with `python3 -c "import fitz; ..."` instead. Same PyMuPDF code, just via terminal.
- **`search_files` may timeout on this project**: Use `read_file` with offset/limit or `terminal` with `find` instead.
- **Read in chunks, not the whole file**: A 30-page chapter produces ~2000 lines of text. Read at offsets: `offset=1` (title/overview), `offset=400` (mid-section), `offset=800` (later sections), `offset=1200` (end/algorithms). 4-5 reads of 100-150 lines each capture the full structure without burning context.
- **Session tool limit is real**: A full chapter (download + extract + 4-5 reads + write spine + patch tracker) consumes ~8-12 tool calls. Plan accordingly; if a chapter is large (34+ pages, 110K+ chars), consider stopping after the write and doing the tracker update in the next session.
- **Do not create markdown task files**: Tasks go to Paperclip issues only. The `07-Tasks/` directory convention is obsolete.
- **Do not create new top-level directories**: Ask in `#bot-backroom` before writing any new directory under `claude-projects/`.
- **Check `DIRECTORY-POLICY.md`**: Read it before creating directories or cloning repos.
- **Verify PDF exists before extracting**: `ls -lh /tmp/slp3-ch{N}.pdf` before opening with fitz.
- **Preserve equations**: Mathematical notation in PDFs may render poorly in text extraction. Verify key equations manually.
- **Update tracker before dispatching**: Always update the tracker before sending Discord messages to maintain consistency.

## Session Reference

- **SLP3 Ingestion (2026-06-05)** — Ingested Chapters 18–22: CFGs & Constituency Parsing, Dependency Parsing, Information Extraction, Semantic Role Labeling, Lexicons for Sentiment/Affect/Connotation. Created 5 knowledge spine entries. Chapter 23 (Coreference Resolution) downloaded and partially read; not yet written to spine. Tracker: `slp3-ingestion-tracker.md`.
- **Refined spine format**: Each entry now includes Overview, numbered sections, Historical Evolution table, Edgeless Relevance & Applications table, and Actionable Tasks list. This emerged from Chapter 18+ and is the canonical format going forward.
- **Chapters 18–22 completed**: `context-free-grammars-constituency-parsing.md`, `dependency-parsing.md`, `information-extraction.md`, `semantic-role-labeling.md`, `lexicons-sentiment-affect-connotation.md`
- **Chapter 23**: In progress (PDF downloaded, text extracted, spine entry pending — session hit tool limit before completion)
- **Prior batch**: Chapters 2–11 + A (HMM Appendix) + 12 + 17–22 (full run from 2026-05-28 to 2026-06-05)
- **Remaining**: Chapters 23, 24, 25, and Appendices B–K
