---
name: ops-alert
description: "Edgeless starter skill: ops-alert"
version: 1.0.0
author: Edgeless
license: MIT
metadata:
  hermes:
    tags: [ops, alert, incident, edgeless, swarm]
    related_skills: [monitoring, triage, review]
---

# Ops Alert Skill

## Overview

Use this skill when responding to operational alerts, incidents, or anomalies.

## When to Use

- Cron job fails or goes silent
- Error logs spike
- User reports a system problem
- Monitoring detects an anomaly

## Workflow

1. **Acknowledge**: Confirm the alert and timestamp
2. **Assess**: Severity, scope, user impact
3. **Investigate**: Gather logs, state, recent changes
4. **Mitigate**: Stop the bleeding if possible
5. **Report**: Document what happened and why

## Severity Levels

- **SEV1**: Complete outage, all hands
- **SEV2**: Major degradation, immediate fix
- **SEV3**: Minor issue, fix within 24h
- **SEV4**: Cosmetic or low-priority, queue

## Investigation Commands

```bash
# Check cron health
hermes cron status
hermes cron list

# Check recent errors
tail -n 200 ~/.hermes/logs/errors.log

# Check disk space
df -h

# Check running processes
ps aux | grep -E "hermes|python"
```

## Post-Incident

- Write a brief post-mortem
- Identify root cause
- Propose preventive measures
- Update runbooks if needed

## Verification

- [ ] Alert acknowledged with timestamp
- [ ] Severity assessed correctly
- [ ] Root cause identified or escalated
- [ ] Mitigation applied
- [ ] Post-mortem written for SEV1/2
