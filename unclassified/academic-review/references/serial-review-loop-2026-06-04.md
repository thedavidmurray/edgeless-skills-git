# Serial Review Loop for Agentic Quality Assurance

**Date:** 2026-06-04
**Context:** Edgeless Lab autonomous security research pipeline
**Related:** `academic-paper` skill, `academic-research` skill, `subagent-orchestration` skill (ensemble consensus)

## 5-Stage Pipeline

```
Stage 1: DRAFT    → Agent writes the finding as structured report
Stage 2: REVIEW   → Another agent reviews for correctness, completeness, clarity
Stage 3: REVISE   → Draft agent addresses feedback
Stage 4: VALIDATE → (Optional) External validation or PoC verification
Stage 5: DECIDE   → Bug bounty / Academic paper / Responsible disclosure / Reject
```

**Agent Assignment:**
| Stage | Agent | Role | Why |
|-------|-------|------|-----|
| 1 | Scribe | Draft report | Writing agent, owns the finding |
| 2 | Beau | Peer review | Critical evaluation, adversarial mindset |
| 3 | Scribe | Revise | Original author, best positioned to fix |
| 4 | Kilo | Validate | Technical validation, PoC verification |
| 5 | Beau | Decide | Editorial judgment, publication routing |

**Paperclip Integration:**
- Each finding creates a Paperclip issue with prefix `SEC-`
- Each stage creates a sub-task with the issue as parent
- Agents assigned based on availability (load-balanced)
- Final decision triggers: bounty report / academic paper / disclosure report

## Stage 1: Draft

**Input:** Raw finding from ensemble audit (consensus-level)

**Prompt:**
```
Write a comprehensive security finding report.

TARGET: {target_name}
COMPONENT: {component}
SEVERITY: {severity}
TITLE: {title}

Structure:
1. Executive Summary — one paragraph, severity, impact, affected versions
2. Technical Details — exact location, root cause, code snippets, PoC
3. Impact Assessment — what attacker can do, business/money impact, affected users
4. Recommendation — specific fix with code example, mitigation strategy, timeline
5. References — related CVEs, papers, prior art, tool output

Style: Project Zero, Trail of Bits, Zellic.
```

**Output:** Structured report with all sections

## Stage 2: Review

**Input:** Draft report

**Prompt:**
```
You are a peer reviewer for a top-tier security conference (USENIX, IEEE S&P, CCS).

Evaluate the following report on:
1. Correctness — Is the vulnerability real? Is the PoC valid?
2. Completeness — Is every claim supported by evidence?
3. Clarity — Is the report understandable by a non-expert?
4. Novelty — Is this a known issue or genuinely new?
5. Impact — Is the severity assessment accurate?
6. Remediation — Is the fix correct and complete?

Return:
## Overall Assessment
- ACCEPT, MINOR REVISION, MAJOR REVISION, or REJECT

## Strengths
- What the report does well

## Weaknesses
- What's missing or incorrect

## Specific Questions
- Questions that must be answered

## Required Changes
- Specific changes to make

Be rigorous. A false positive is worse than a missed finding.
```

**Output:** Structured review with verdict

## Stage 3: Revise

**Input:** Draft report + Review feedback

**Prompt:**
```
Revise the following security finding report based on peer review feedback.

ORIGINAL REPORT:
{draft}

PEER REVIEW FEEDBACK:
{review}

Make ALL requested changes. Address every question. Strengthen weak arguments.
Do not dismiss feedback — if a reviewer is confused, the report needs to be clearer.

Return the complete revised report.
```

**Output:** Revised report

## Stage 4: Validate

**Input:** Revised report

**Activities:**
- Re-run the PoC to verify it still works
- Check that the fix suggestion compiles
- Verify CVSS score calculation
- Cross-check against known databases (CVE, bug bounty programs)

**Output:** Validation report with yes/no on each check

## Stage 5: Decide

**Input:** Validated report

**Prompt:**
```
You are the editorial board of Edgeless Lab.

Decide the publication path for this finding:

{report}

Consider:
1. BUG_BOUNTY — Is there a bug bounty program? Is the bounty size worth the effort? ($10k+ minimum)
2. ACADEMIC_PAPER — Is the finding novel enough for a paper? Is there related work to compare against?
3. RESPONSIBLE_DISCLOSURE — No bounty program, but maintainers need to know. 90-day timeline.
4. REJECT — False positive, known issue, or too low impact.

Return:
## Decision
- BUG_BOUNTY, ACADEMIC_PAPER, RESPONSIBLE_DISCLOSURE, or REJECT

## Rationale
- Why this path

## Timeline
- When to disclose

## Next Steps
- Specific actions
```

**Output:** Publication decision

## Integration with Ensemble Consensus

**Pre-filter:** Before entering the serial review loop, findings must pass the ensemble consensus filter from `subagent-orchestration`:
- Only findings found by ≥2 independent auditors are reviewed
- This prevents wasting review cycles on hallucinations
- The audit engine runs 4 auditors with different angles; consensus filters false positives

**Post-filter:** After the serial review loop, findings are categorized by decision:
- `BUG_BOUNTY` → Auto-generate HackerOne/Bugcrowd report
- `ACADEMIC_PAPER` → Use `academic-paper` 12-agent pipeline to generate LaTeX
- `RESPONSIBLE_DISCLOSURE` → Generate disclosure report, notify maintainers
- `REJECT` → Log to false-positive database, feed back to auditor tuning

## Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Review cycle time | <24h per finding | Paperclip timestamps |
| Acceptance rate | 60-70% | Decisions logged |
| Revision iterations | 1-2 | Review loop stage count |
| False positive rate | <20% | Rejected findings vs total |
| Academic papers/quarter | 1-2 | Decision = ACADEMIC_PAPER |
| Bounty submissions/quarter | 3-5 | Decision = BUG_BOUNTY |

## When to Use

**Use the serial review loop when:**
- Findings have real-world consequences (money, security, safety)
- Publication is planned (academic or bounty)
- Stakes are high enough that a false positive is worse than a missed finding
- Multiple stakeholders need to review

**Skip the serial review loop when:**
- Internal exploration or preliminary findings
- Time-sensitive triage (use the sentry, not the review loop)
- Low-stakes content (documentation, internal notes)
- The finding is already confirmed by a human expert

## Integration with academic-paper Skill

For `ACADEMIC_PAPER` decisions:

1. **Draft agent** (`academic-paper` Phase 4) uses the finding report as input
2. **Structure agent** (`academic-paper` Phase 2) designs paper structure around the finding
3. **Literature agent** (`academic-paper` Phase 1) searches for related work
4. **Peer review** (`academic-review` 7-agent panel) reviews the paper before submission
5. **Revision coach** (`academic-paper` revision mode) addresses feedback
6. **Formatter** (`academic-paper` Phase 7) generates LaTeX for arXiv submission

This creates a dual-track pipeline:
- **Fast track:** Security findings → ensemble audit → serial review → bug bounty (days)
- **Slow track:** Novel findings → ensemble audit → serial review → academic paper → peer review → publication (weeks-months)

## Paperclip Task Structure

```
Issue: SEC-001: Reentrancy vulnerability in Uniswap V4 swap router
├── Sub-task: Draft report (assigned to Scribe)
├── Sub-task: Peer review (assigned to Beau)
├── Sub-task: Revision (assigned to Scribe)
├── Sub-task: Validation (assigned to Kilo)
└── Sub-task: Publication decision (assigned to Beau)
```

---

**File location:** `~/.hermes/skills/academic-review/references/serial-review-loop-2026-06-04.md`
