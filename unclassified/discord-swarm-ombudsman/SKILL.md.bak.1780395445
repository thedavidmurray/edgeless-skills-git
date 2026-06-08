---
name: discord-swarm-ombudsman
title: Discord Swarm Coordination Audit (Ombudsman Agent)
version: 1.2
description: >
  Monitor Discord bot-to-bot communication channels to identify stale coordination
  threads, unacknowledged work assignments, and coordination loops that need closing.
  Generates triage reports and posts actionable next steps to #bot-backroom.
  Designed to run as a scheduled cron job for multi-agent swarm health monitoring.
  v1.2: Added zombie task detection (in_progress tasks with 0 working agents).
author: Hive
requirements:
  - hermes-agent >= 0.9.0
  - discli (Discord CLI tool)
  - Access to #audit-log, #bot-backroom, #alerts channels
scripts:
  - parse_coordination.py: Parse bot-backroom messages for structured tag staleness
  - edga_claim_analyzer.py: Analyze audit-log for duplicate/silent/awaiting claims
---

# Discord Swarm Ombudsman — Coordination Audit

## Purpose

The Ombudsman agent monitors bot-to-bot coordination channels and identifies where
communication has stalled. Unlike the Active Dispatcher (which assigns work), the
Ombudsman audits whether assigned work is being acknowledged and progressed.

**Scope:**
- Detect work assignments >2h old with no `[TYPE:ACK]` response
- Identify escalation requests pending without resolution
- Spot onboarding messages without confirmation
- Summarize findings and propose next actions
- Post triage reports to #bot-backroom

**Non-scope:**
- Does not assign new work (that's the Dispatcher)
- Does not fix technical issues (that's the respective specialists)
- Does not monitor Paperclip API directly (that's Fleet Analyzer)

## When to Use

Run this skill when:
1. **Scheduled cron execution** — Every 4 hours to maintain swarm health
2. **Human suspects coordination breakdown** — Bots not responding to each other
3. **Post-incident** — After resolving a message storm or loop, verify cleanup
4. **Pre-handoff** — Before human goes offline, ensure no pending coordination

## Prerequisites

```bash
# Verify discli is available
which discli && discli --version

# Required channel IDs (customize for your server)
AUDIT_LOG_CHANNEL=1463668475078901896
BOT_BACKROOM_CHANNEL=1498530774062858240
ALERTS_CHANNEL=1463668223667998972
```

## Execution Workflow

### Step 1: Read Coordination Channels

```bash
# Read recent messages from audit-log (use -n not --limit)
discli msg read $AUDIT_LOG_CHANNEL -n 50 --format json > /tmp/audit_log.json

# Read recent messages from bot-backroom
discli msg read $BOT_BACKROOM_CHANNEL -n 40 --format json > /tmp/backroom.json

# Read recent messages from alerts (for escalation context)
discli msg read $ALERTS_CHANNEL -n 20 --format json > /tmp/alerts.json
```

### Step 3: Parse for Structured Tags AND Natural Language Claims

**Important:** Agents post in both structured tags AND natural language. Parse both:

| Pattern | Meaning | Check For | Where Found |
|---------|---------|-----------|-------------|
| `\[FROM:(\w+)\]` | Sender identity | — | #bot-backroom |
| `\[TO:(\w+)\]` | Target recipient | — | #bot-backroom |
| `\[TYPE:(\w+)\]` | Message purpose | `ASSIGNED`, `EXECUTE`, `ACK`, `COMPLETE` | #bot-backroom |
| `\[REF:([\w-]+)\]` | Reference ID | Staleness check | #bot-backroom |
| `(?i)claimed.*edga-\d+` | Agent claiming work | Duplicate claims, claim storms | #audit-log |
| `(?i)deliverable.*complete.*edga-\d+` | Work completed | Status progression | #audit-log |
| `(?i)blocked.*edga-\d+` | Work blocked | Dependency issues | #audit-log |
| `(?i)stand down.*edga-\d+` | Claim released | Resolution events | #audit-log |
| `(?i)error.*syntax\|failure.*script` | Script failures | Infrastructure issues | #audit-log |
| `EDGA-\d{3,4}` | Issue reference | Cross-message threading | Both channels |

**Use the provided script for automated detection:**
```bash
python3 ~/.hermes/skills/.archive/discord-swarm-ombudsman/scripts/edga_claim_analyzer.py \
  /tmp/audit_log.json /tmp/backroom.json
```

This outputs:
- JSON analysis to `/tmp/edga_analysis.json`
- Discord-ready triage report to `/tmp/triage_report.txt`
- Character count verification for the 2000-char limit

### Step 3: Identify Stale Threads

**Stale Criteria (from real-world observation):**

| Category | Threshold | Condition | Example from Field |
|----------|-----------|-----------|-------------------|
| **Duplicate claims** | Any overlap | Same EDGA-XXX claimed by multiple agents | EDGA-783: edgeless-cc 3x + kilo 6x |
| **Silent claim** | >3 hours | Claim posted, no updates since | EDGA-850 at 01:33, silent at 04:00+ |
| **Delivered, awaiting approval** | >2 hours | `[TYPE:COMPLETE]` or deliverable posted, human decision pending | EDGA-847 Phase 1 awaiting AVA download approval |
| **Agent created but idle** | >2 hours | Agent ID created, skill provisioning not started | EDGA-851 Studio agent idle at 02:05 |
| **Script/infrastructure failure** | Any | Error messages about scanner/dispatcher failures | Ombudsman SyntaxError at 07:01 |
| **Stand down processed** | Recently | Claim released after double-claim detected | EDGA-307 stand down at 10:50 |
| **Work assignment** | >2 hours | `[TYPE:ASSIGNED]` without `[TYPE:ACK]` | Per protocol |
| **Onboarding** | >2 hours | `[TYPE:WELCOME]` without `[TYPE:ACK][DEPTH:1]` | Per protocol |
| **Escalation** | >2 hours | `[TYPE:ESCALATE]` without resolution | Per protocol |
| **Human question** | >4 hours | Human @mention to bot with no response | Per protocol |
| **Standby loop risk** | >30 min | Multiple exit messages between bots | Per protocol |
| **Amplification loop** | Any | `DISCORD_ALLOW_BOTS=all` + bot system messages causing 100+ msg/min cascade | See `hermes-multi-agent-discord/references/backroom-amplification-prevention.md` |

**Detection Logic (Extended):**

```python
def is_stale(msg, current_time, all_messages):
    """Check if a message represents a stale coordination thread."""
    content = msg.get("content", "")
    timestamp = parse(msg.get("timestamp", ""))
    age_hours = (current_time - timestamp).total_seconds() / 3600
    author = msg.get("author", {}).get("username", "unknown")
    
    # Extract REF/EDGA ID
    ref_match = re.search(r'EDGA-(\d{3,4})', content, re.IGNORECASE)
    ref_id = f"EDGA-{ref_match.group(1)}" if ref_match else None
    
    # Extract claim patterns from #audit-log natural language
    claim_match = re.search(r'(?i)(claimed|claiming).{0,50}edga-\d+', content)
    is_claim = bool(claim_match)
    
    # Check for actionable tags (#bot-backroom structured)
    actionable_types = ["ASSIGNED", "EXECUTE", "ARCH", "ENRICH", "VPS", "TRIAGE", "WELCOME"]
    has_actionable = any(f"[TYPE:{t}]" in content for t in actionable_types)
    has_ack = "[TYPE:ACK]" in content
    has_complete = "[TYPE:COMPLETE]" in content or "complete" in content.lower()
    is_blocked = "BLOCKED" in content or "blocked" in content.lower()
    is_stand_down = "stand down" in content.lower() or "releasing claim" in content.lower()
    is_deliverable = "deliverable" in content.lower() or "delivered" in content.lower()
    is_script_error = "syntaxerror" in content.lower() or "script failed" in content.lower()
    is_idle = "idle" in content.lower() or "awaiting activation" in content.lower()
    
    # PATTERN 1: Duplicate claims (CRITICAL - same task, multiple agents)
    if ref_id and is_claim:
        other_claims = [
            m for m in all_messages 
            if re.search(rf'EDGA-{ref_match.group(1)}', m.get("content", ""), re.IGNORECASE)
            and re.search(r'(?i)(claimed|claiming)', m.get("content", ""))
            and m.get("author", {}).get("username") != author
        ]
        if len(other_claims) > 0:
            return {
                "type": "duplicate_claims",
                "ref": ref_id,
                "agents": list(set([m.get("author", {}).get("username") for m in other_claims] + [author])),
                "claim_count": len(other_claims) + 1,
                "action_required": "Clarify ownership — first claimer leads, others assist or release"
            }
    
    # PATTERN 2: Silent claim (claimed but no updates for >3h)
    if is_claim and not has_complete and not is_stand_down and age_hours > 3:
        # Check for any follow-up messages on same EDGA by same author
        follow_ups = [
            m for m in all_messages
            if re.search(rf'EDGA-{ref_match.group(1)}', m.get("content", ""), re.IGNORECASE)
            and m.get("author", {}).get("username") == author
            and parse(m.get("timestamp", "")) > timestamp
        ]
        if len(follow_ups) == 0:
            return {
                "type": "silent_claim",
                "ref": ref_id,
                "agent": author,
                "claim_time": timestamp,
                "age_hours": age_hours,
                "action_required": "Status update or release claim"
            }
    
    # PATTERN 3: Delivered, awaiting human decision
    if is_deliverable and "awaiting" in content.lower() and age_hours > 2:
        return {
            "type": "awaiting_approval",
            "ref": ref_id,
            "agent": author,
            "delivered_at": timestamp,
            "action_required": "Human approval/decision needed"
        }
    
    # PATTERN 4: Agent created but idle
    if is_idle and "agent" in content.lower() and age_hours > 2:
        return {
            "type": "idle_agent",
            "ref": ref_id,
            "agent_created": author,
            "action_required": "Activate skill provisioning or schedule work"
        }
    
    # PATTERN 5: Script/infrastructure failure
    if is_script_error:
        return {
            "type": "infrastructure_failure",
            "ref": ref_id,
            "failed_component": "scanner/dispatcher/script",
            "action_required": "Fix script syntax or infrastructure"
        }
    
    # PATTERN 6: Standard work assignment without acknowledgment (#bot-backroom)
    if has_actionable and not has_ack and not has_complete and age_hours > 2:
        return {
            "type": "stale_assignment",
            "ref": ref_id,
            "target": extract_to(content),
            "sender": extract_from(content),
            "age_hours": age_hours,
            "action_required": "ACK or reassignment"
        }
    
    # PATTERN 7: Amplification loop (bot-to-bot message storm)
    is_system_noise = any(phrase in content for phrase in [
        "Max retries", "Rate limited", "Interrupting current task",
        "Gateway shutting down", "HTTP 429", "HTTP 426", "Standing by.",
        "[SILENT", "retry/system message"
    ])
    if is_system_noise and author_bot:
        # Count how many similar messages in last 5 minutes
        recent_noise = [
            m for m in all_messages
            if any(p in m.get("content", "") for p in ["Max retries", "Rate limited", "HTTP 429"])
            and (current_time - parse(m.get("timestamp", ""))).total_seconds() < 300
        ]
        if len(recent_noise) > 10:
            return {
                "type": "amplification_loop",
                "ref": None,
                "agents": list(set(m.get("author", {}).get("username") for m in recent_noise)),
                "noise_count": len(recent_noise),
                "action_required": "EMERGENCY: Stop all gateways, set DISCORD_ALLOW_BOTS=mentions, restart one at a time"
            }
    
    return None
```

### Step 4: Generate Triage Report

Format the findings as a structured report with all stale pattern types:

```
[FROM:Ombudsman][TO:Hive][TYPE:TRIAGE][REF:OMBU-{timestamp}]

## Stale Coordination Loop Report — #{channel} Scan

**Scan Time:** {ISO8601}  
**Window:** Last {N} messages from #{channel}  
**Stale Threshold:** Bot messages >4h old without human response / work assignments without acknowledgment

---

### 🔴 Top Priority Patterns

| ID | Task | Agent(s) | Issue | Blocker | Proposed Action |
|---|---|---|---|---|---|
| 1 | EDGA-XXX | Agent A + Agent B | **DUPLICATE CLAIMS** | Coordination failure | Clarify ownership: first claimer leads |
| 2 | EDGA-XXX | Agent A | Silent claim >3h | No updates | Status update or release |
| 3 | EDGA-XXX | Agent A | Delivered, awaiting approval | Human decision | Approve/decline Phase X |
| 4 | EDGA-XXX | Agent A | Agent created, **IDLE** | Activation pending | Activate skill provisioning |
| 5 | — | — | Script failure | scan-audit-log.sh SyntaxError | Fix scanner script |
| 6 | EDGA-XXX | Agent A | **RESOLVED** — stand down | Double-claim resolved | No action needed |
| 7 | — | Multiple bots | **AMPLIFICATION LOOP** | `DISCORD_ALLOW_BOTS=all` | Emergency stop → `mentions` → restart |

---

### 📊 Summary Statistics

- **Total stale threads:** {N}
- **Duplicate claims:** {N} (coordination failure risk)
- **Amplification loops:** {N} (bot-to-bot message storm)
- **Script failures:** {N} (infrastructure)
- **Idle awaiting activation:** {N} (resources not utilized)
- **Awaiting human decision:** {N} (approval bottlenecks)
- **Resolved during scan:** {N} (self-healing events)

**Most urgent:** {specific recommendation}

[STATUS:COMPLETE]
```

**Alternative condensed format** (if message length limit concerns):

```
[FROM:Ombudsman][TO:Hive][TYPE:TRIAGE][REF:OMBD-{id}]

### 🔴 {Pattern Type}: EDGA-XXX
**Agents:** {list} | **Issue:** {brief} | **Action:** {recommendation}

### 🟡 {Pattern Type}: EDGA-XXX
**Agent:** {name} | **Since:** {time} | **Action:** {recommendation}
...

**Summary:** {N} stale, {N} critical, {N} resolved | **Urgent:** {top item}
```

### Step 5: Post to #bot-backroom

```bash
# Check character count first (Discord limit: 2000)
wc -c /tmp/triage_report.txt

# If >2000, use condensed format (see Pitfalls section)
# Post report
discli msg send $BOT_BACKROOM_CHANNEL "$(cat /tmp/triage_report.txt)"
```

**Alternative for long reports:** Post summary first, then details as follow-up thread replies.

## Reference: Channel Definitions

| Channel | ID | Purpose | What to Look For |
|---------|-----|---------|------------------|
| `#audit-log` | 1463668475078901896 | Cron reports, system status | Claim messages, status reports |
| `#bot-backroom` | 1498530774062858240 | Bot-to-bot coordination | `[TYPE:ASSIGNED]`, `[TYPE:ACK]`, `[TYPE:COMPLETE]` |
| `#alerts` | 1463668584650334248 | Errors, escalations | Critical notifications, swarm alerts |

## Critical Cross-System Coordination Failures

### Zombie Task State (NEW — v1.2)

**Pattern:** Tasks marked `in_progress` in Paperclip but `0 agents working`

| Signal | API Check | Escalation |
|--------|-----------|------------|
| Dashboard shows `X in progress` + `0 working` | Query `/companies/{id}/issues` vs agent `current_task` | 🔴 CRITICAL |
| `in_progress` > 0 && `working_agents` == 0 | Cross-reference both endpoints | 🔴 CRITICAL |
| Phantom task accumulation | Tasks "in progress" for >24h with no agent activity | 🟡 WARNING |

**Detection Logic:**
```python
# Check for zombie state
issues = fetch_paperclip_issues(status="in_progress")  # 54 tasks
agents = fetch_paperclip_agents()
working = sum(1 for a in agents if a.get("current_task"))

if len(issues) > 0 and working == 0:
    # 🔴 CRITICAL: Zombie task queue
    escalate_to_alerts(
        pattern="zombie_tasks",
        severity="critical",
        count=len(issues),
        action="Investigate agent claiming mechanism"
    )
```

**Root Causes:**
- Agent claiming mechanism broken (tasks pulled to in_progress but no agent picks up)
- Cron job failure (agent activation jobs not running)
- API endpoint drift (dashboard uses `/companies/{id}/issues`, agents use `/agents`)

## Reference: Message Type Meanings

| Type | Expect Response | Timeout | Escalate If... |
|------|-----------------|---------|---------------|
| `[TYPE:ASSIGNED]` | `[TYPE:ACK]` within 2h | 2 hours | No ACK, no status |
| `[TYPE:EXECUTE]` | `[TYPE:ACK]` then `[TYPE:COMPLETE]` | 2h ACK, varies for complete | Stalled mid-work |
| `[TYPE:ARCH]` | `[TYPE:ACK]` then `[TYPE:COMPLETE]` | 2h ACK, varies for complete | Stalled mid-work |
| `[TYPE:ENRICH]` | `[TYPE:ACK]` then `[TYPE:COMPLETE]` | 2h ACK, varies for complete | Stalled mid-work |
| `[TYPE:VPS]` | `[TYPE:ACK]` then `[TYPE:COMPLETE]` | 2h ACK, varies for complete | Stalled mid-work |
| `[TYPE:WELCOME]` | `[TYPE:ACK][DEPTH:1]` | 2 hours | Reaction but no text ACK |
| `[TYPE:ESCALATE]` | `[TYPE:STATUS]` or resolution | 2 hours | No response |
| `[TYPE:TRIAGE]` | `[TYPE:STATUS]` | 2 hours | No coordinator response |
| `[TYPE:ZOMBIE]` | Immediate human triage | Immediate | Tasks orphaned mid-flight |

## Common Blockers to Document

When reporting stale threads, identify the likely blocker:

| Blocker Pattern | Meaning | Suggested Action |
|-----------------|---------|------------------|
| `DEPENDS_ON killed task-XXX` | Dependency on cancelled work | Clear dependency, reassess |
| `Missing [TYPE:ACK]` | Bot hasn't confirmed receipt | Ping bot, verify gateway health |
| `Reaction but no text ACK` | Partial onboarding compliance | Request full protocol compliance |
| `No Paperclip issues assigned` | Empty work queue | Verify dispatcher is running |
| `Gateway error in logs` | Technical connectivity issue | Escalate to Beau/VPS |

## Pitfalls & Fixes

### Discord 2000 Character Limit
Discord messages are limited to 2000 characters. Long triage reports will fail with:
```
Discord API error 400: {"message": "Invalid Form Body", "code": 50035,
"errors": {"content": {"_errors": [{"code": "BASE_TYPE_MAX_LENGTH",
"message": "Must be 2000 or fewer in length"}]}}}
```

**Fix:** Condense reports into a compact format:
```
[FROM:Ombudsman][TO:Hive][TYPE:TRIAGE][REF:OMBU-{timestamp}]
**Stale Scan** ({time} UTC, {N} msgs)

🔴 **CRITICAL:**
• **{REF}**: {agents} ({age}h) → Action: {brief}

🟡 **SILENT:**
• **{REF}**: {agent} ({age}h silent) → Action: {brief}

🟢 **AWAITING ({count}):**
{list}

**Summary**: {N} flagged | Most urgent: {top}
[STATUS:COMPLETE]
```

Use `wc -c` to check character count before posting.

## Cron Setup

```bash
# Run every 4 hours
0 */4 * * * hermes run --agent ombudsman --skill discord-swarm-ombudsman
```

Or as a standalone script:

```bash
#!/bin/bash
# ombudsman_cron.sh
export DISCORD_AUDIT_LOG_CHANNEL=1463668475078901896
export DISCORD_BACKROOM_CHANNEL=1498530774062858240
export DISCORD_ALERTS_CHANNEL=1463668223667998972

hermes run --agent ombudsman --skill discord-swarm-ombudsman --quiet
```

## Integration with Active Dispatcher

The Ombudsman complements the Active Dispatcher:

| System | Trigger | Action |
|--------|---------|--------|
| **Active Dispatcher** | New unassigned issues | Posts `[TYPE:ASSIGNED]` to #bot-backroom |
| **Ombudsman** | Stale `[TYPE:ASSIGNED]` >2h | Posts `[TYPE:TRIAGE]` to #bot-backroom |
| **Coordinator (Hive)** | `[TYPE:TRIAGE]` received | Reassigns, pings, or escalates |

## Expected Output

A successful Ombudsman run produces:
1. **Zero findings** → Silent completion (no spam)
2. **Stale threads found** → Triage report in #bot-backroom
3. **Critical issues** → Additional `[TYPE:ESCALATE]` to #alerts

## Changelog

- **v1.1** (2026-04-29): Added `edga_claim_analyzer.py` script for automated EDGA pattern detection; fixed discli flag (`-n` not `--limit`); added Discord 2000-char limit pitfall; condensed triage report format example
- **v1.0** (2026-04-29): Initial skill — Discord channel monitoring, stale thread detection, triage report generation
