---
name: triage
description: "Edgeless starter skill: triage"
version: 1.0.0
author: Edgeless
license: MIT
metadata:
  hermes:
    tags: [triage, backlog, prioritization, edgeless, swarm]
    related_skills: [planning, monitoring, ops-alert]
---

# Triage Skill

## Overview

Use this skill to prioritize, categorize, and route incoming tasks and issues.

## When to Use

- New issues or requests arrive
- Backlog needs periodic review
- User asks "what should I work on next?"
- Emergency or interruption occurs

## Workflow

1. **Ingest**: Collect all new items
2. **Score**: Urgency + impact + effort
3. **Categorize**: Bug, feature, research, ops, docs
4. **Route**: Assign to right agent or queue
5. **Communicate**: Report decisions clearly

## Scoring Matrix

| Urgency | Impact | Effort | Priority |
|---------|--------|--------|----------|
| High    | High   | Low    | P0 — Do now |
| High    | Medium | Medium | P1 — Today |
| Medium  | High   | High   | P2 — This week |
| Low     | Low    | Low    | P3 — Backlog |

## Routing Rules

- Code/bug → Kilo
- Infra/research → Beau
- Docs/knowledge → Scribe
- Architecture/review → Edgeless CC
- Trading → Pamela
- Audit/quality → Critic
- Coordination → Hive

## Verification

- [ ] Every item has a priority
- [ ] Every item has an owner
- [ ] Stale items (>7 days) flagged
- [ ] P0 items have immediate action
