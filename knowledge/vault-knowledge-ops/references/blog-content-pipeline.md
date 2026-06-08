# Blog Content Pipeline: Vault-to-Published

A 6-stage file-based pipeline that turns vault knowledge into platform-ready blog content. Triggered by the overnight blog topic miner, reviewed by a multi-agent council, and gated by an autoreason scoring tournament.

## Pipeline Stages

```
01-Frameworks  →  02-Drafts  →  03-Autoreason  →  04-Council  →  05-Prepped  →  06-Published
   (Hive)         (Scribe)       (Hive)           (Multi)       (Hive)         (David)
```

### Stage 1: Frameworks

Overnight miner samples two ChromaDB collections from different semantic domains, finds the strongest conceptual bridge via LLM, and writes a structured framework:
- TITLE, THESIS, HOOK
- 5 SECTIONS with 2-3 bullet points each
- SOURCES (vault refs)
- ANGLE (who it's for)
- CONFIDENCE (high/medium/low)

Script: `~/claude-projects/scripts/overnight_blog_topic_miner.py`
Output: `claude-vault/07-Business/Blog-Pipeline/01-Frameworks/`

### Stage 2: Drafts

Scribe (or assigned writer) expands the framework into a 1200-2500 word draft matching David's voice: direct, decisive, numbered lists, no filler enthusiasm.

Acceptance criteria:
- Opening hook matches framework
- All 5 sections expanded with concrete examples
- At least 2 vault sources cited with [[wiki-style links]]
- Ends with clear CTA
- Voice passes the "would David say this" test

Task files: `02-Drafts/task-NNN-draft.md` with `status: pending|in_progress|done`

### Stage 3: Autoreason Tournament

Multi-model scoring shootout on 4 dimensions (0-25 each):
| Dimension | What it measures |
|-----------|-----------------|
| clarity | Reader can follow without re-reading |
| voice_match | Sounds like David wrote it |
| source_depth | Vault sources used meaningfully |
| actionability | Reader can act on this today |

**A-grade threshold: 80/100**

If below A-grade, the model rewrites the draft. The improved draft is written to 
the autoreason result file. **Critical:** do NOT automatically re-score the 
improved draft with the same model — reasoning models produce unreliable scores on 
their own output (either hallucinating low scores from parsing their own reasoning 
text, or inflating scores via self-approval). Skip the re-score and mark it TBD 
for the council stage to verify.

**Prompt lock rules for the improvement step:**
```
- Output ONLY the rewritten draft text. No explanations, no reasoning, no commentary.
- Do not include score discussions or analysis.
- Do not wrap the output in markdown code blocks.
- Start with the title as a # heading.
- End with --- and a sources line.
```

Even with these rules, reasoning models still leak chain-of-thought. Always 
pair prompt rules with `clean_improved_draft()` post-processing (see 
`references/llm-output-cleaning.md`).

Script: `~/claude-projects/scripts/blog_autoreason_tournament.py`
Output: `03-Autoreason/task-NNN-autoreason.md`

### Stage 4: Council Interrogation

Three-lens review by the swarm:
- **Edgeless CC** — Architecture lens: does the argument hold structurally? Is the thesis defensible?
- **Kilo** — Technical lens: are claims accurate? Do code examples compile?
- **Scribe** — Knowledge lens: sources cited correctly? Depth sufficient?

Each writes 150-250 words. Edgeless CC consolidates into a revision checklist.

Script: `~/claude-projects/scripts/blog_council_interrogation.py`
Reviews dir: `04-Council/task-NNN-reviews/`

### Stage 5: Prepped

Platform-specific formatting with content sanitization applied (see `references/content-sanitization-rules.md`):

1. **Beehiiv** — full blog with H2 headings, internal links, CTA
2. **X thread** — 5-7 tweet thread summarizing thesis
3. ~~LinkedIn~~ — skipped per user preference (technical content does not perform well on LinkedIn)

Pre-flight checklist:
- Title optimized (SEO + curiosity)
- Meta description (160 chars)
- Featured image prompt generated
- Internal links added
- CTA clear
- **Content sanitized** — swarm bot names scrubbed, internal codes removed, "wetware" kept if applicable
- `status: ready_for_approval`

### Stage 6: Published

Human approval gate. David gives thumbs-up or requests revision. Once approved, the post moves here and the task is closed.

## Orchestration

The `blog_pipeline_orchestrator.py` script polls all stages and auto-advances tasks when `status: done` is detected. Run manually or via cron every 30-60 minutes.

```bash
cd ~/claude-projects && python3 scripts/blog_pipeline_orchestrator.py
```

## Fallback When Paperclip Is Down

When Paperclip (port 3100) is unavailable, the pipeline falls back to file-based task tracking:
1. Task files live in stage directories with YAML frontmatter
2. `status: pending` → `in_progress` → `done` tracked in markdown
3. Orchestrator scans for status changes and creates next-stage files
4. No external task system required

This was validated 2026-05-21 when Paperclip server was unresponsive.

## Idempotency

- Frameworks use content-hash deduplication (`content_hash` in frontmatter)
- Autoreason skips if result file already exists
- Council only creates review tasks once per agent
- Orchestrator checks for existing files before creating duplicates
