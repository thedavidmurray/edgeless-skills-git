---
name: proof-of-completion
title: Proof of Completion — EFC Scoring for Agent Harnesses
version: 1.0.0
description: >
  Every agent completion must report an EFC (Effective Feedback Compute) scorecard.
  EFC credits feedback only when it is Informative, Valid, Non-redundant, and Retained.
  This skill defines the scoring protocol and the reporting format required for every
  agent output in the Edgeless swarm.
author: Hive
requirements:
  - hermes-agent >= 0.9.0
  - EFC framework (arXiv:2605.29682)
---

# Proof of Completion — EFC Scoring

## Purpose

The **Effective Feedback Compute (EFC)** framework (Zhang et al., arXiv:2605.29682) provides a trace-level scaling coordinate for agent harnesses. Instead of measuring raw tokens or tool calls, EFC measures only feedback that is actually useful: **Informative**, **Valid**, **Non-redundant**, and **Retained**.

This skill mandates that **every agent completion in the Edgeless swarm** report a 4-bit EFC scorecard. The scorecard is used by the Hive dispatcher to normalize by task demand and improve harness quality under fixed budget.

## The Four EFC Criteria

| Criterion | Question | Pass if … |
|-----------|----------|-----------|
| **Informative** | Did the feedback provide new information that moves the task forward? | The output contains at least one novel fact, reasoning step, or actionable item not present in the prior context. |
| **Valid** | Is the feedback factually correct and logically sound? | No hallucinations, no contradictions with known ground truth, and all tool outputs are interpreted correctly. |
| **Non-redundant** | Does the feedback avoid restating what is already in the working memory or prior turns? | The output is not a verbatim or near-verbatim repeat of earlier agent messages, tool results, or prompt context. |
| **Retained** | Is the feedback structured so it can be retained for subsequent decisions? | The output is tagged, referenced, or stored in a way that downstream agents or memory layers can retrieve it. |

## Scorecard Format

Every completion must end with a YAML block:

```yaml
---
efc_scorecard:
  informative: yes   # yes / no
  valid: yes         # yes / no
  non_redundant: yes # yes / no
  retained: yes      # yes / no
  task_demand: medium # low / medium / high (set by task_demand.py classifier)
  harness_depth: H3   # H1–H6 (recommended by dispatcher)
  agent: <agent_name>
  timestamp: <ISO8601>
  trace_id: <uuid>
---
```

## Self-Assessment Rules

1. **Informative** — If the agent only acknowledges receipt ("OK", "Got it"), mark `no`.
2. **Valid** — If any tool call failed and the agent did not surface the error correctly, mark `no`.
3. **Non-redundant** — If >50% of the output is restatement of prior context, mark `no`.
4. **Retained** — If the output is not written to working memory, Chroma, or a structured artifact, mark `no`.

## Integration with Hive Dispatch

- The dispatcher reads `efc_scorecard` from the last turn of each agent trace.
- Traces with `informative: no` or `valid: no` are flagged for re-generation or human review.
- Traces with `non_redundant: no` trigger deduplication in `swarm_working_memory`.
- Traces with `retained: no` are auto-persisted to the `swarm_working_memory` Chroma collection.

## Example: Good Completion

```markdown
# Analysis: Peter Thiel's Zero to One philosophy

[… substantive analysis …]

---
efc_scorecard:
  informative: yes
  valid: yes
  non_redundant: yes
  retained: yes
  task_demand: medium
  harness_depth: H3
  agent: soul_analyst
  timestamp: 2026-05-29T14:30:00Z
  trace_id: 7f3a9b2c-4d1e-4f8a-9c3b-2e5d6f7a8b9c
---
```

## Example: Bad Completion (flagged)

```markdown
Got it, I will proceed.

---
efc_scorecard:
  informative: no
  valid: yes
  non_redundant: no
  retained: no
  task_demand: low
  harness_depth: H1
  agent: generic_ack
  timestamp: 2026-05-29T14:31:00Z
  trace_id: a1b2c3d4-e5f6-7890-abcd-ef1234567890
---
```

## References

- Zhang, X., Wang, D., Xu, K., Zhu, Q., & Che, W. (2026). *Scaling Laws for Agent Harnesses via Effective Feedback Compute*. arXiv:2605.29682.
