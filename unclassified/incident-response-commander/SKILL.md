---
name: incident-response-commander
description: Production incident management, severity classification, structured response coordination, blameless post-mortems, SLO/SLI tracking, and on-call process design. Turns chaos into structured resolution.
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [incident-response, sre, post-mortem, on-call, reliability, monitoring]
    related_skills: [system-health, self-healing-filter, telegram-ops-alerting]
    requires_toolsets: [terminal, send_message, cronjob]
---

# Incident Response Commander

Production incident commander. Coordinates structured response, establishes severity frameworks, runs blameless post-mortems, and builds the on-call culture that keeps systems reliable and engineers sane.

## When to Use

- A production service is down or degraded
- You need to classify severity and coordinate response
- Post-mortem facilitation after an incident
- Designing on-call rotations and SLO frameworks
- Building runbooks for known failure scenarios
- Supervisor storm or gateway crash (Hermes-specific)

## Severity Classification Matrix

| Level | Name | Criteria | Response Time | Update Cadence | Escalation |
|-------|------|----------|---------------|----------------|------------|
| SEV1 | Critical | Full outage, data loss risk, security breach | < 5 min | Every 15 min | VP Eng + CTO immediately |
| SEV2 | Major | Degraded for >25% users, key feature down | < 15 min | Every 30 min | Eng Manager within 15 min |
| SEV3 | Moderate | Minor feature broken, workaround available | < 1 hour | Every 2 hours | Team lead next standup |
| SEV4 | Low | Cosmetic issue, no user impact | Next business day | Daily | Backlog triage |

**Auto-escalation triggers:**
- Impact scope doubles -> upgrade one level
- No root cause after 30 min (SEV1) or 2 hours (SEV2) -> escalate
- Any data integrity concern -> immediate SEV1

## Hermes-Specific Incident Patterns

### Supervisor Storm (Most Common)

**Symptoms:** Multiple bots killed simultaneously by SIGTERM from launchd, high load average, restart loops.

**Detection:**
```bash
# Check supervisor logs
~/.hermes/profiles/beau/scripts/discord-sentry-interactive-watchdog.sh

# Check recent kills
grep "signal=SIGTERM" ~/.hermes/profiles/*/logs/gateway-shutdown-diag.log

# Check load average
grep "loadavg" ~/.hermes/profiles/*/logs/gateway.error.log | tail -5
```

**Response:**
1. Clear storm state: `rm -f ~/.hermes/profiles/<name>/.clean_shutdown`
2. Extend threshold in `hermes-bot-supervisor.sh` (>3 restarts in 60 min)
3. Add startup grace period (45s)
4. Restart affected gateways

### Gateway Crash Loop

**Symptoms:** Gateway starts, dies within seconds, repeats.

**Detection:**
```bash
# Check exit reason
cat ~/.hermes/profiles/<name>/gateway_state.json

# Check recent errors
tail -50 ~/.hermes/profiles/<name>/logs/errors.log
```

**Response:**
1. Read `gateway_state.json` for exit reason
2. Check `errors.log` for specific error pattern
3. If auth issue: verify `.env` credentials
4. If config issue: check `config.yaml` syntax
5. If resource issue: check `hermes doctor`

### Paperclip API Outage

**Symptoms:** All Paperclip-dependent crons fail, task creation fails.

**Detection:**
```bash
curl -sS http://127.0.0.1:3100/api/health
timeout 5 bash -c 'cat < /dev/tcp/127.0.0.1/3100'
```

**Response:**
1. Check if Paperclip process is running
2. If stopped: restart Paperclip service
3. If port conflict: identify conflicting process
4. Fallback: queue tasks to file-based dispatch

## Structured Response Process

### Step 1: Detect & Declare (0-5 min)

1. Validate it's a real incident (not false positive)
2. Classify severity using matrix above
3. Declare in designated channel with:
   - Severity level
   - Impact description
   - Who is Incident Commander
4. Assign roles:
   - **IC (Incident Commander):** Owns timeline and decisions
   - **Tech Lead:** Drives diagnosis
   - **Scribe:** Logs actions with timestamps
   - **Comms Lead:** Sends stakeholder updates

### Step 2: Coordinate Response (5-30 min)

```bash
# IC commands (examples for Hermes swarm)
"Beau: check system status and report"
"Kilo: investigate Paperclip connectivity"
"Hive: coordinate with Discord #bot-backroom"
```

**Rules:**
- Timebox hypotheses: 15 min per path, then pivot
- Log every action in real-time (not from memory later)
- Communicate status at fixed intervals even if "no change"
- Document in incident channel as source of truth

### Step 3: Mitigate & Verify (30 min - resolution)

1. Apply mitigation FIRST, root cause later:
   - Rollback bad deploy
   - Scale up capacity
   - Restart service
   - Enable feature flag
2. Verify recovery through metrics, not visual check
3. Monitor for 15-30 min post-mitigation
4. Declare resolved with all-clear communication

### Step 4: Post-Mortem (within 48 hours)

**Template:**
```markdown
# Post-Mortem: [Incident Title]

**Date:** YYYY-MM-DD
**Severity:** SEV[1-4]
**Duration:** [start] -- [end] ([total])
**IC:** [name]

## Executive Summary
[2-3 sentences: what happened, who was affected, how resolved]

## Impact
- Users affected: [number or %]
- Revenue impact: [estimated or N/A]
- SLO budget consumed: [X%]

## Timeline (UTC)
| Time | Event |
|------|-------|
| 14:02 | Alert fires: API error rate > 5% |
| 14:05 | On-call acknowledges |
| 14:08 | Incident declared SEV2, IC assigned |
| ... | ... |

## Root Cause
### What happened
[Technical explanation]

### Contributing Factors
1. Immediate cause: [trigger]
2. Underlying cause: [why trigger was possible]
3. Systemic cause: [organizational gap]

## 5 Whys
1. Why did service go down? -> [answer]
2. Why did [answer 1] happen? -> [answer]
3. ... -> [root systemic issue]

## What Went Well
- [Things that worked]

## What Went Poorly
- [Things that slowed response]

## Action Items
| ID | Action | Owner | Priority | Due | Status |
|----|--------|-------|----------|-----|--------|
| 1 | [Action] | [Owner] | P1 | [Date] | Not Started |

## Lessons Learned
[Key takeaways for architecture and process]
```

## Hermes Tool Integration

### System Status Check

```bash
# Quick health check across all profiles
for profile in beau hive kilo scribe edgeless-cc; do
    echo "=== $profile ==="
    cat ~/.hermes/profiles/$profile/gateway_state.json 2>/dev/null | grep -E '"gateway_state"|"platforms"'
done
```

### Log Analysis

```bash
# Find recent errors across all bots
find ~/.hermes/profiles -name "errors.log" -mtime -1 -exec tail -20 {} \;

# Search for specific error pattern
grep -r "SIGTERM" ~/.hermes/profiles/*/logs/ | tail -20
```

### Paperclip Incident Tracking

```python
from hermes_tools import terminal

# Create incident tracking issue
result = terminal("""
curl -sS -X POST "http://127.0.0.1:3100/api/companies/c5ea22fb-99d2-46a1-87c6-e7fc1ab0d712/issues" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "[SEV2] Hermes gateway storm - multiple bots killed",
    "description": "Incident tracking. See post-mortem link.",
    "priority": "high",
    "status": "in_progress",
    "labels": ["incident", "sev2", "supervisor"]
  }'
""")
```

### Telegram Alerting

```python
from hermes_tools import send_message

# Send incident notification
send_message(
    target="telegram",
    message="[SEV2] Hermes gateway storm detected. 5 bots killed by supervisor. Investigating."
)
```

## Pitfalls

1. **Never skip severity classification.** It determines escalation, communication cadence, and resource allocation.
2. **Always assign roles before troubleshooting.** Chaos multiplies without coordination.
3. **Document actions in real-time.** A Slack thread or channel is the source of truth, not memory.
4. **Timebox hypotheses:** 15 minutes per path, then pivot.
5. **Mitigate first, root cause later.** Fix the bleeding before analyzing why.
6. **Verify recovery through metrics.** "Looks fine" is not sufficient -- confirm SLIs are within SLO.
7. **Never frame post-mortems as blame.** Frame as "the system allowed this failure mode."
8. **Untested runbooks are false security.** Test quarterly.
9. **SLOs must have teeth.** When error budget is burned, feature work pauses for reliability work.
10. **On-call engineers must have authority.** No multi-level approval chains for emergency actions.

## Verification Checklist

| Step | Command | Success Criteria |
|------|---------|-----------------|
| 1. Detect | Check gateway_state.json | Identify affected bots |
| 2. Classify | Assess impact scope | Assign SEV level |
| 3. Declare | Post to Discord/Telegram | Roles assigned |
| 4. Investigate | Check logs, metrics | Root cause hypothesis |
| 5. Mitigate | Execute fix | Metrics recover |
| 6. Verify | Monitor 15-30 min | No regression |
| 7. Post-mortem | Create within 48h | Action items tracked |

## Example: Supervisor Storm Response

```markdown
---
Incident: Supervisor storm kills 5 bots
Detected: 2026-05-21 16:58 UTC
Severity: SEV2 (swarm availability degraded)
IC: Beau
---

## Timeline
16:58 - Launchd sends SIGTERM to jojo, hive, kilo, scribe, edgeless-cc
16:59 - Load average 227.41 detected
17:00 - Beau detects storm pattern in logs
17:02 - Clear .clean_shutdown flags
17:05 - Restart all affected gateways
17:10 - All 5 bots confirmed running
17:15 - Monitor for 15 minutes, no further kills
17:30 - Declare resolved

## Root Cause
Supervisor threshold too low (3 restarts/60 min) with no startup grace period.
Load spike from runaway cron caused cascading kills.

## Action Items
1. Raise supervisor threshold to 5/60 min (P1, Beau, today)
2. Add 45s startup grace period (P1, Beau, today)
3. Implement manual-restart exemption (P1, Kilo, this week)
4. Add storm backoff (15 min) (P2, Kilo, next week)
```

## Related Skills

- `system-health` -- Health checks and monitoring
- `self-healing-filter` -- Automated rule learning for alerts
- `telegram-ops-alerting` -- Alert delivery and formatting
