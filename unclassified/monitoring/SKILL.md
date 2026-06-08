---
name: monitoring
description: "Edgeless starter skill: monitoring"
version: 1.0.0
author: Edgeless
license: MIT
metadata:
  hermes:
    tags: [monitoring, health, ops, edgeless, swarm]
    related_skills: [ops-alert, triage, review]
---

# Monitoring Skill

## Overview

Use this skill to check system health, cron job status, and infrastructure state.

## When to Use

- User asks "is everything OK?"
- Cron job reports silent failure
- Before and after deployments
- Weekly health checks

## Workflow

1. **Inventory**: List what should be running
2. **Check**: Verify each component
3. **Log**: Capture status and anomalies
4. **Alert**: Report issues, not just OKs
5. **Track**: Maintain history for trend detection

## Checks

- `hermes cron status` — scheduler health
- `hermes cron list` — job states
- Disk space on Mac and VPS
- Recent error logs in `~/.hermes/logs/`
- Expected output files are updating

## Silent Failure Detection

Not all [SILENT] returns are healthy. Check:
- Cron runs every hour but last output > 24h old
- Expected files not updating in vault/
- Queue files not growing despite activity
- Scripts referenced in docs don't exist

## Verification

- [ ] All expected jobs have recent output
- [ ] No errors in logs
- [ ] Disk space > 20%
- [ ] Any silent failures explained
