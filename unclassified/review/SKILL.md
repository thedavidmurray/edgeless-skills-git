---
name: review
description: "Edgeless starter skill: review"
version: 1.0.0
author: Edgeless
license: MIT
metadata:
  hermes:
    tags: [review, audit, quality, edgeless, swarm]
    related_skills: [critic, coding, docs]
---

# Review Skill

## Overview

Use this skill to review code, docs, plans, and decisions. Be rigorous, not polite.

## When to Use

- Code review before merge
- Document review before publishing
- Plan review before execution
- Post-mortem or retrospective

## Review Checklist

### Code
- [ ] Correctness: Does it do what it claims?
- [ ] Security: Any injection, escape, or leak risks?
- [ ] Tests: Covered? Edge cases handled?
- [ ] Style: Consistent with codebase?
- [ ] Performance: Any obvious inefficiency?

### Docs
- [ ] Accuracy: No outdated or false claims
- [ ] Completeness: All needed sections present
- [ ] Clarity: Readable by intended audience
- [ ] Links: All references resolve

### Plans
- [ ] Feasibility: Realistic given constraints
- [ ] Completeness: All dependencies noted
- [ ] Risk: Failure modes considered
- [ ] Ownership: Every task assigned

## Output Format

```markdown
# Review: [Item]

## Status
APPROVED / CHANGES_REQUESTED / NEEDS_DISCUSSION

## Issues
1. **[Severity]**: Description → Suggested fix

## Questions
What needs clarification

## Praise
What is done well
```

## Verification

- [ ] Every issue has severity
- [ ] Suggested fixes are concrete
- [ ] Review is actionable, not vague
- [ ] Author can proceed without guessing
