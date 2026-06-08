---
name: academic-paper
description: "12-agent academic paper writing pipeline with 6 modes (plan/full/outline/revision/revision-coach/abstract). IMRaD/Literature Review/Theoretical/Case Study/Policy Brief/Conference Paper types. APA/Chicago/MLA/IEEE/Vancouver citations. LaTeX/DOCX/PDF/Markdown output. Bilingual abstracts. Style calibration + writing quality checks. Integrates with arxiv skill."
version: 1.0.0
author: Kilo (ported from Imbad0202/ARS)
license: MIT
metadata:
  hermes:
    tags: [Academic, Paper, Writing, Research, LaTeX, Citations, IMRaD]
    related_skills: [arxiv, academic-research, academic-review]
    toolsets: [web, file, terminal, code_execution]
---

# Academic Paper — 12-Agent Paper Writing Pipeline

Ported from ARS v3.7.1 to Hermes skill format. General-purpose academic paper writing across all disciplines.

## Quick Start

```
write a paper on AI impact on higher education
skill_view(name='academic-paper', mode='plan')  # Socratic guidance mode
skill_view(name='academic-paper', mode='full')  # Full 8-phase pipeline
```

## Modes

| Mode | Trigger | Description |
|------|---------|-------------|
| `plan` | "guide my paper", "help me plan" | Socratic dialogue + INSIGHT extraction |
| `full` | "write paper", "academic paper" | 8-phase pipeline with IRON RULE checkpoints |
| `outline-only` | "paper outline", "outline" | Structure only, no drafting |
| `revision` | "revise paper", "parse reviews" | Revision roadmap from reviewer comments |
| `revision-coach` | "revision coach" | Standalone coach mode |
| `abstract` | "write abstract" | Bilingual abstract generation only |
| `product-report` | "write a report", "product report", "shareable report" | Full pipeline producing a proof-of-concept product report with competitive analysis, implementation, results, and economic validation. Uses the same 12-agent pipeline but with product-focused framing.

## 12-Agent Pipeline

| # | Agent | Phase | Role |
|---|-------|-------|------|
| 1 | `intake_agent` | 0 | Configuration interview, handoff detection |
| 2 | `literature_strategist_agent` | 1 | Search strategy, source screening |
| 3 | `structure_architect_agent` | 2 | Paper structure, outline, word allocation |
| 4 | `argument_builder_agent` | 3 | Claim-evidence chains, logical flow |
| 5 | `draft_writer_agent` | 4 | Section-by-section drafting |
| 6 | `citation_compliance_agent` | 5a | Citation format verification |
| 7 | `abstract_bilingual_agent` | 5b | Bilingual abstract (zh-TW + EN) |
| 8 | `peer_reviewer_agent` | 6 | Simulated 5-dimension review |
| 9 | `formatter_agent` | 7 | LaTeX/DOCX/PDF/Markdown output |
| 10 | `socratic_mentor_agent` | Plan | Chapter-by-chapter guidance |
| 11 | `visualization_agent` | 4/7 | Publication-ready figure code |
| 12 | `revision_coach_agent` | Revision | Parse comments → roadmap |

## Paper Types

- **IMRaD**: Empirical research (5,000-8,000 words)
- **Literature Review**: Synthesis (6,000-10,000 words)
- **Theoretical**: Framework analysis (5,000-8,000 words)
- **Case Study**: In-depth analysis (4,000-7,000 words)
- **Policy Brief**: Evidence-based recommendations (2,000-4,000 words)
- **Conference Paper**: Concise presentation (2,000-5,000 words)
- **Product Report**: Proof-of-concept documentation with competitive analysis, implementation, and economic validation (3,000-6,000 words). Uses IMRaD structure but framed for business/product audiences. Use when the user asks to "write a report" or "document the product" and wants the rigor of academic style applied to product work.

## Citation Formats

APA 7th (default), Chicago 17th, MLA 9th, IEEE, Vancouver

## Output Formats

- **LaTeX**: .tex + .bib for journal submission
- **DOCX**: Via Pandoc for Word workflows
- **PDF**: Via LaTeX or Pandoc
- **Markdown**: Native, universal

## Integration with arxiv Skill

```python
# Literature search uses existing arxiv skill
skill_view(name='arxiv')  # For arXiv papers
# Semantic Scholar API for citations/related papers
# (see arxiv skill for SS API patterns)
```

## Orchestration: 8-Phase Workflow

```
Phase 0: CONFIG       -> intake_agent          -> Paper Configuration Record
Phase 1: RESEARCH     -> literature_strategist -> Search Strategy + Corpus
Phase 2: ARCHITECTURE  -> structure_architect   -> Outline + Evidence Map
Phase 3: ARGUMENTATION -> argument_builder      -> Argument Blueprint
Phase 4: DRAFTING      -> draft_writer          -> Complete Draft
Phase 5a: CITATIONS    -> citation_compliance  -> Citation Audit
Phase 5b: ABSTRACT     -> abstract_bilingual   -> Bilingual Abstract (parallel)
Phase 6: PEER REVIEW   -> peer_reviewer         -> Review Report (max 2 loops)
Phase 7: FORMAT        -> formatter             -> Final Output
```

## IRON RULE Checkpoints (Hermes `clarify`)

| Checkpoint | Rule |
|------------|------|
| Phase 0 -> 1 | User must confirm Paper Configuration Record |
| Phase 2 -> 3 | User must approve outline |
| Phase 6 | Max 2 revision loops; unresolved -> "Acknowledged Limitations" |
| Critical issues | Block progression to Phase 7 |

## Style Calibration

Optional: Provide 3+ past papers during intake. Pipeline learns writing voice (sentence rhythm, vocabulary, citation style) and applies as soft guide during drafting.

## Writing Quality Check

Applied during draft self-review:
- Flag AI-typical terms (25-term list)
- Em dash check (≤3 total)
- Semicolon density (≤2 per 1000 words)
- Remove throat-clearing openers
- Sentence length variation
- Paragraph length by function
- Binary contrast usage (≤2 per paper)

## Mode: Plan (Socratic)

When user says "guide my paper" or "help me plan":
1. Simplified 3-question interview
2. Handoff to socratic_mentor_agent
3. Chapter-by-chapter guidance through 4 convergence signals
4. INSIGHT extraction at each layer

## Mode: Revision-Coach

Standalone mode for reviewer comments:
1. Parse unstructured comments
2. Classify: Critical/Major/Minor/Suggestion
3. Map to sections
4. Prioritize
5. Output Revision Roadmap

## Usage Examples

```python
# Full paper with default settings
skill_view(name='academic-paper', mode='full', topic="AI in higher education QA")

# Plan mode for guidance
skill_view(name='academic-paper', mode='plan', topic="declining birth rates + private universities")

# Revision mode
skill_view(name='academic-paper', mode='revision', reviewer_comments="...")

# Abstract only
skill_view(name='academic-paper', mode='abstract', paper_draft="...")
```

## Subagent Delegation Pattern

```python
# Phase 0: Intake
delegate_task(
    goal="Conduct paper configuration interview",
    context={"mode": "plan|full", "user_input": "..."},
    toolsets=["web", "session_search"]
)

# Phase 4: Drafting
delegate_task(
    goal="Write full paper draft section-by-section",
    context={
        "config": {...},
        "outline": {...},
        "argument_blueprint": {...},
        "bibliography": {...}
    },
    toolsets=["file", "code_execution"]
)
```

## References

- `agents/intake_agent.md` - Configuration interview
- `agents/draft_writer_agent.md` - Full-text drafting
- `agents/peer_reviewer_agent.md` - Simulated review
- `agents/formatter_agent.md` - Output formatting
- `agents/socratic_mentor_agent.md` - Plan mode guidance
- `agents/revision_coach_agent.md` - Revision roadmap

## Source Attribution

Ported from: https://github.com/Imbad0202/academic-research-skills
Original: ARS (Academic Research Skills) v3.7.1 by Imbad0202
