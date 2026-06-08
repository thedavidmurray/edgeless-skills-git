---
name: academic-review
description: "7-agent peer review simulation for academic papers. Simulated double-blind review with 5-dimension scoring (originality, rigor, significance, clarity, ethics). Structured review reports with revision suggestions. Can parse existing reviewer comments into structured roadmap. Integrates with academic-paper revision mode."
version: 1.0.0
author: Kilo (ported from Imbad0202/ARS)
license: MIT
metadata:
  hermes:
    tags: [Peer-Review, Academic-Review, Paper-Review, Revision-Roadmap]
    related_skills: [academic-paper, academic-research]
    toolsets: [file, web]
---

# Academic Review — 7-Agent Peer Review Simulation

Ported from ARS academic-paper-reviewer to Hermes skill format. Simulated double-blind peer review for academic papers.

## Quick Start

```
review this paper for me
simulate peer review of my draft
evaluate my manuscript
```

## 5-Dimension Scoring

| Dimension | Score Range | Criteria |
|-----------|-------------|----------|
| **Originality** | 1-10 | Novel contribution, gap addressing |
| **Rigor** | 1-10 | Methodology soundness, evidence quality |
| **Significance** | 1-10 | Field impact, practical relevance |
| **Clarity** | 1-10 | Organization, writing, accessibility |
| **Ethics** | Pass/Fail | Compliance, attribution, dual-use |

**Verdict**: Accept (avg ≥8), Minor Revision (6-7.9), Major Revision (4-5.9), Reject (<4)

## 7-Agent Pipeline

| # | Agent | Role |
|---|-------|------|
| 1 | `intake_reviewer_agent` | Paper intake, configuration |
| 2 | `methodology_evaluator_agent` | Methods assessment |
| 3 | `argument_assessor_agent` | Logic, claims, evidence chains |
| 4 | `evidence_evaluator_agent` | Citation quality, source credibility |
| 5 | `writing_quality_agent` | Style, clarity, organization |
| 6 | `synthesis_reviewer_agent` | Cross-dimension integration |
| 7 | `revision_planner_agent` | Priority-structured revision roadmap |

## Review Report Structure

```markdown
## Review Report: [Paper Title]

### Overall Verdict: [Accept/Minor/Major/Reject]
### Composite Score: [X.X/10]

### Dimension Scores
| Dimension | Score | Weight | Rationale |
|-----------|-------|--------|-----------|
| Originality | X/10 | 25% | ... |
| Rigor | X/10 | 25% | ... |
| Significance | X/10 | 25% | ... |
| Clarity | X/10 | 25% | ... |

### Critical Issues (Blockers)
1. [Issue] -> [Section] -> [Fix suggestion]

### Major Concerns
1. [Concern] -> [Suggested revision]

### Minor Suggestions
1. [Suggestion]

### Revision Roadmap
| Priority | Item | Section | Approach |
|----------|------|---------|----------|
| P0 | ... | ... | ... |
| P1 | ... | ... | ... |
```

## Revision Roadmap Format

When reviewing or parsing existing comments:

```markdown
## Revision Roadmap

### Critical (Must Fix)
| # | Original Comment | Section | Specific Fix |
|---|------------------|---------|--------------|
| 1 | "..." | 3.2 | Add control group justification |

### Major (Should Fix)
| # | Original Comment | Section | Approach |
|---|------------------|---------|----------|
| 1 | "..." | 4.1 | Expand discussion |

### Minor (Polish)
| # | Original Comment | Section | Quick Fix |
|---|------------------|---------|-----------|
| 1 | "..." | 2.3 | Rephrase |

### Acknowledged Limitations
Items identified but not addressed due to scope/constraints.
```

## Integration with academic-paper

```python
# Phase 6 of academic-paper invokes peer review
# Then Phase 4 revision addresses feedback

# Standalone review mode
skill_view(name='academic-review', paper_draft="...")

# Parse existing comments
skill_view(name='academic-review', mode='parse', 
           reviewer_comments="... unstructured text ...")
```

## Sprint Contract Protocol (v3.6.2+)

For structured reviews, implements paper-blind/paper-visible splits:

1. **Pre-commitment**: Reviewers specify evaluation criteria before seeing paper
2. **Paper-visible scoring**: Apply criteria consistently
3. **Physical separation**: Prevents rationalization drift

## Usage Examples

```python
# Full review simulation
skill_view(name='academic-review', 
           paper_draft="[full paper text or markdown file path]")

# Parse existing reviewer comments
delegate_task(
    goal="Parse unstructured reviewer comments into structured revision roadmap",
    context={"comments": "...", "paper_outline": "..."},
    toolsets=["file"]
)

# Targeted review (specific dimension)
delegate_task(
    goal="Evaluate methodology section rigor",
    context={"paper": "...", "focus": "methodology"},
    toolsets=["file"]
)
```

## Subagent Delegation

```python
# Complete review panel simulation
delegate_task(
    goal="Conduct 5-dimension peer review with revision roadmap",
    context={"paper": "...", "discipline": "..."},
    toolsets=["file"]
)

# Methodology deep-dive
delegate_task(
    goal="Assess methodology rigor, validity threats, alternatives",
    context={"methods_section": "...", "paradigm": "quantitative/qualitative/mixed"},
    toolsets=["web", "file"]
)
```

## Serial Review Loop (Agentic Quality Gate)

For findings, reports, or research outputs that need rigorous vetting before publication — especially security research, policy analysis, or any work with real-world consequences.

**Stages:**

```
Stage 1: DRAFT    → Agent writes the finding as structured report
Stage 2: REVIEW   → Another agent reviews for correctness, completeness, clarity
Stage 3: REVISE   → Draft agent addresses feedback
Stage 4: VALIDATE → (Optional) External validation or PoC verification
Stage 5: DECIDE   → Bug bounty / Academic paper / Responsible disclosure / Reject
```

**Paperclip Integration:**
- Each finding creates a Paperclip issue (`SEC-` prefix)
- Each stage creates a sub-task
- Agents assigned based on availability (load-balanced)
- Final decision triggers the appropriate publication workflow

**Prompt Templates:**

```python
# Stage 1: Draft
"Write a comprehensive security finding report.\n\nTARGET: {target}\nCOMPONENT: {component}\nSEVERITY: {severity}\n\nStructure: Executive Summary, Technical Details, Impact Assessment, Recommendation, References."

# Stage 2: Review
"You are a peer reviewer for a top-tier security conference.\n\nReview the following report for: Correctness, Completeness, Clarity, Novelty, Impact, Remediation.\n\nReturn: ACCEPT, MINOR REVISION, MAJOR REVISION, or REJECT."

# Stage 3: Revision
"Revise the following report based on peer review feedback.\n\nORIGINAL REPORT: ...\nPEER REVIEW FEEDBACK: ...\n\nMake ALL requested changes. Address every question."

# Stage 4: Decision
"You are the editorial board. Decide the publication path for this finding.\n\nConsider: Bug Bounty (is there a program?), Academic Paper (is it novel?), Responsible Disclosure (no bounty, 90-day timeline), Reject (false positive or too low impact)."
```

**Ensemble Consensus Pre-Filter:**
Before entering the serial review loop, findings must pass the ensemble consensus filter from the `subagent-orchestration` skill — only findings found by ≥2 independent auditors are reviewed. This prevents wasting review cycles on hallucinations.

**Integration with academic-paper skill:**
For findings routed to `ACADEMIC_PAPER`, the draft agent uses the `academic-paper` 12-agent pipeline to generate LaTeX. The review agent uses the `academic-review` 7-agent peer review panel. The revise agent uses the `revision_coach_agent`. This creates a dual-track: one for rapid security findings, one for publication-quality academic papers.

**When to use the Serial Review Loop:**
- Security findings (bug bounty, responsible disclosure)
- Academic papers (pre-submission review)
- Policy reports (stakeholder review)
- Product audits (internal review before public release)
- Any finding where a false positive is worse than a missed finding

**When NOT to use:**
- Internal brainstorming or exploration
- Preliminary findings (too early for rigor)
- Low-stakes content (documentation, internal notes)
- Time-sensitive triage (use the sentry, not the review loop)

## References

- `references/serial-review-loop-2026-06-04.md` — Full 5-stage pipeline with Paperclip integration
- `references/directed-prompting-2026-06-04.md` — Zcash audit case study (in `subagent-orchestration` skill)
- `agents/intake_reviewer_agent.md` — RQ formulation
- `agents/methodology_evaluator_agent.md` — Methods assessment
- `agents/argument_assessor_agent.md` — Logic, claims, evidence chains
- `agents/evidence_evaluator_agent.md` — Citation quality, source credibility
- `agents/writing_quality_agent.md` — Style, clarity, organization
- `agents/synthesis_reviewer_agent.md` — Cross-dimension integration
- `agents/revision_planner_agent.md` — Priority-structured revision roadmap

## Source Attribution

Ported from: https://github.com/Imbad0202/academic-research-skills
Original: ARS academic-paper-reviewer v3.6.x by Imbad0202
