---
name: research-paper-writing
title: Research Paper Writing Pipeline
description: End-to-end pipeline for writing ML/AI research papers — from experiment design through analysis, drafting, revision, and submission. Covers NeurIPS, ICML, ICLR, ACL, AAAI, COLM.
version: 1.2.0
author: Orchestra Research
license: MIT
dependencies: [semanticscholar, arxiv, habanero, requests, scipy, numpy, matplotlib, SciencePlots]
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Research, Paper Writing, Experiments, ML, AI, NeurIPS, ICML, ICLR, ACL, AAAI, COLM, LaTeX, Citations, Statistical Analysis]
    category: research
    related_skills: [arxiv, ml-paper-writing, subagent-driven-development, plan]
    requires_toolsets: [terminal, files]

---

# Research Paper Writing Pipeline

End-to-end pipeline for producing publication-ready ML/AI research papers targeting **NeurIPS, ICML, ICLR, ACL, AAAI, and COLM**.

**This is not a linear pipeline** — it is an iterative loop. Results trigger new experiments. Reviews trigger new analysis.

## Pipeline Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    RESEARCH PAPER PIPELINE                  │
│                                                             │
│  Phase 0: Project Setup ──► Phase 1: Literature Review      │
│       │                          │                          │
│       ▼                          ▼                          │
│  Phase 2: Experiment     Phase 5: Paper Drafting ◄──┐      │
│       Design                     │                   │      │
│       │                          ▼                   │      │
│       ▼                    Phase 6: Self-Review      │      │
│  Phase 3: Execution &           & Revision ──────────┘      │
│       Monitoring                 │                          │
│       │                          ▼                          │
│       ▼                    Phase 7: Submission               │
│  Phase 4: Analysis ─────► (feeds back to Phase 2 or 5)     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## When To Use This Skill

- **Starting a new research paper** from an existing codebase or idea
- **Designing and running experiments** to support paper claims
- **Writing or revising** any section of a research paper
- **Preparing for submission** to a specific conference
- **Responding to reviews** with additional experiments
- **Writing non-empirical papers** — theory, survey, benchmark (see `paper-types.md`)

## Core Philosophy

1. **Be proactive.** Deliver complete drafts, not questions. Scientists are busy — produce concrete drafts they can react to.
2. **Never hallucinate citations.** AI-generated citations have ~40% error rate. Always fetch programmatically.
3. **Paper is a story, not a collection of experiments.** Every paper needs one clear contribution stated in a single sentence.
4. **Experiments serve claims.** Every experiment must state which claim it supports.
5. **Commit early, commit often.** Git log is the experiment history.

## Quick Reference: Proactivity Levels

| Confidence | Action |
|------------|--------|
| **High** | Write full draft, deliver, iterate on feedback |
| **Medium** | Write draft with flagged uncertainties, continue |
| **Low** | Ask 1-2 targeted questions via `clarify`, then draft |

## Phase Documentation

Each phase has detailed reference documentation in `references/`:

| Phase | Reference | Description |
|-------|-----------|-------------|
| Phase 0 | `phase-0-project-setup.md` | Explore repo, organize workspace, identify contribution |
| Phase 1 | `phase-1-literature-review.md` | Search papers, verify citations, build .bib file |
| Phase 2 | `phase-2-experiment-design.md` | Design experiments with explicit claim mapping |
| Phase 3 | `phase-3-execution-monitoring.md` | Run experiments, track progress, monitor costs |
| Phase 4 | `phase-4-result-analysis.md` | Statistical analysis, visualization, LaTeX tables |
| Phase 5 | `phase-5-paper-drafting.md` | Write all sections with venue-specific style |
| Phase 6 | `phase-6-self-review.md` | Simulate reviewers, checklists, revision |
| Phase 7 | `phase-7-submission.md` | Format checks, final PDF, checklist |
| Phase 8 | `phase-8-post-acceptance.md` | Camera-ready, posters, code release |

**Start with Phase 0 for new projects.** Use `view` to read phase references as needed.

## Quick Commands

**Explore repository:**
```bash
ls -la
find . -name "*.py" | head -30
find . -name "*.md" -o -name "*.txt" | xargs grep -l -i "result\|conclusion\|finding"
```

**Literature search (Semantic Scholar):**
```python
# Use semanticscholar API
response = requests.get(f"https://api.semanticscholar.org/graph/v1/paper/search",
    params={"query": "your topic", "fields": "title,authors,year,citationCount,openAccessPdf", "limit": 10})
```

**Statistical testing:**
```python
from scipy import stats
# Paired t-test for comparing two methods
t_stat, p_value = stats.ttest_rel(method_a_scores, method_b_scores)
```

## Resources

### references/
Complete phase-by-phase documentation covering:
- Detailed step-by-step procedures
- LaTeX templates for each conference
- Statistical analysis patterns
- Citation verification workflows
- Review response strategies

### assets/
Templates for:
- LaTeX paper templates (NeurIPS, ICML, ACL, etc.)
- Figure templates
- Experiment tracking spreadsheets

## Venue Quick Links

See `conference-formats.md` for detailed formatting:

| Conference | Page Limit | Style | Anonymous? |
|------------|------------|-------|------------|
| NeurIPS | 9 pages | Single-blind | Yes |
| ICML | 9 pages | Single-blind | Yes |
| ICLR | No limit | Double-blind | Yes |
| ACL | 8 pages | Double-blind | Yes |
| AAAI | 7 pages | Double-blind | Yes |
| COLM | 9 pages | Single-blind | Yes |

## Common Issues and References

| Issue | Reference |
|-------|-----------|
| Can't identify contribution | `phase-0-project-setup.md` |
| Citation verification fails | `phase-1-literature-review.md` |
| Experiment design unclear | `phase-2-experiment-design.md` |
| Cost tracking | `phase-3-execution-monitoring.md` |
| Statistical significance | `phase-4-result-analysis.md` |
| Writing specific section | `phase-5-paper-drafting.md` |
| Pre-submission check | `phase-7-submission.md` |

## Notes

- Pipeline is iterative — expect to loop between phases
- Conference deadlines are hard constraints — plan backward from submission
- Non-empirical papers (theory, survey, position) have different structure — see `paper-types.md`
- Always verify citations programmatically
