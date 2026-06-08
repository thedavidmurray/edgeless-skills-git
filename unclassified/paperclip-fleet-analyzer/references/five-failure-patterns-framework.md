# Five Failure Patterns Framework for Fleet Audits

**Session origin:** 2026-05-03 Paperclip fleet audit (EDGA-1035/1036/1037/1038 creation)  
**Context:** Analyzing 1,031 issues across 21 agents to identify systemic blockers

---

## Overview

When a fleet shows healthy agent status (idle/running) but near-zero velocity, look for these five recurring failure patterns. Each pattern has a signature in the backlog data and a specific unblock action.

---

## Pattern 1: The Authentication Vortex

**Signature:** Cluster of tickets (8-20+) all blocked on the same interactive auth step

**Indicators:**
- Same keyword appears in 10+ issue titles: `notebooklm`, `ssh`, `login`, `OAuth`
- Assignee concentration (one agent type: Scribe, Beau, etc.)
- Status = `blocked` or perpetually `in_progress` with no deliverables
- Common description pattern: "requires manual login", "blocked on auth"

**Example from audit:**
```
35 NotebookLM tickets (EDGA-145, 128, 310, 306, 131, 732-739)
All: "requires notebooklm login"
Assignee: Scribe (40 active issues, mostly this)
Status: in_progress for 16+ days
```

**Unblock:** One 5-minute manual action (run `notebooklm login`, SSH key setup, etc.)

**Prevention:**
- Tag auth-blocked issues with `blocked:auth` label
- Batch auth-blocked issues into single "unblock sweep" ticket
- Schedule recurring auth refresh BEFORE expiration

---

## Pattern 2: The Dependency Pipeline Failure

**Signature:** Technical dependency installed/configured but not wired to actual usage

**Indicators:**
- Package installed (`sentence-transformers`, `chroma`, etc.)
- Service running (ChromaDB on :8100)
- But integration code throws errors or isn't called
- Tickets reference "blocked on X" where X exists

**Example from audit:**
```
EDGA-883: "Run first full vault sync into unified_knowledge"
Blocker: EDGA-924 "Install sentence-transformers"
Reality: Already installed, just never used
Root cause: No one verified pipeline end-to-end
```

**Unblock:** Actually run the integration; verify output; don't trust "installed" = "working"

**Detection:**
```python
# Check for installed-but-unused
if package_installed and not pipeline_ran_in_last_7_days:
    flag_as_pattern_2()
```

---

## Pattern 3: The Noise Cascade

**Signature:** Infrastructure works but creates so much noise it becomes unusable

**Indicators:**
- Bots responding to each other in loops
- Alert fatigue (100+ messages/hour in #general)
- Humans ignoring agent output due to volume
- Agents "working" but no human sees results

**Example from audit:**
```
7-bot Discord swarm
Pattern: @mention → Hermes interrupt → bot response → @mention
Result: 4x circular loop, Fireworks API exhausted
EDGA-989: Fireworks suspension from API spam
EDGA-983: Need cooldown + close-detection
EDGA-999: Need error suppression
```

**Unblock:** Add backpressure (cooldowns), noise gates (error suppression), visibility controls (routing to #bot-backroom not #general)

---

## Pattern 4: The Gap Ticketing Anti-Pattern

**Signature:** Identifying a need, ticketing it, then ticketing it again instead of building it

**Indicators:**
- Multiple tickets with "Skill Gap:" prefix
- Same skill name appears in 5+ tickets
- No skill creation work started
- Tickets are triaged, not executed

**Example from audit:**
```
EDGA-1021: Skill Gap: tradingview-pine-automation (6 trading issues)
EDGA-1020: Skill Gap: mcp-server-scaffold (21 backlog items)
EDGA-1023-1027: More gap tickets for same skills
Pattern: Keep identifying gap, never close it
```

**Unblock:** Stop ticketing gaps. Build the skill. One skill ~2 hours, unblocks 6-21 tickets.

**Rule:** If a skill gap appears in 3+ tickets, convert to skill-creation issue with assignee immediately.

---

## Pattern 5: The External Hardware Block

**Signature:** Ticket requires physical human presence with specific equipment

**Indicators:**
- Description contains "when David is at...", "requires physical...", "hardware needed"
- Status = `blocked` with no ETA
- Assignee = `unassigned` or `null`
- Age > 14 days with zero progress

**Example from audit:**
```
EDGA-946: AxiDraw Calibration — BLOCKED: David at machine
EDGA-947: Multi-Color Pen Plot — BLOCKED: David at machine  
EDGA-948: Photograph & List — BLOCKED: David at machine
Pattern: Cannot progress until operator physically present
```

**Unblock:** Close tickets; reopen when hardware/operator available; preserve documentation; don't let backlog inflate with unactionable work.

---

## Audit Structure Template

When running comprehensive fleet audits, produce output in this structure:

### 1. Fleet Health Snapshot
- Agent count by status
- Workload distribution (active issues per agent)
- Aging analysis (issues >14 days in_progress)

### 2. Velocity Analysis
- Completions by month (detect bulk updates vs organic velocity)
- Current rate vs historical average
- Days to clear backlog at current rate

### 3. Five Patterns Detection
- Pattern 1 (Auth Vortex): Count + list of blocked issues
- Pattern 2 (Dependency Fail): Check installed vs integrated
- Pattern 3 (Noise): Alert/message volume
- Pattern 4 (Gap Ticketing): Skill gap ticket count
- Pattern 5 (Hardware): Physical dependency tickets

### 4. Unblock Actions (Prioritized)
| Priority | Action | Time | Unblocks |
|----------|--------|------|----------|
| Immediate | Manual auth step | 5 min | 12-35 tickets |
| Today | Install + verify pipeline | 30 min | 10-15 tickets |
| This week | Create missing skills | 4 hours | 20-40 tickets |
| This week | Close hardware-blocked | 15 min | 3-5 tickets |

### 5. Swarm Rebalancing
- Overloaded agents (threshold: >25 active)
- Underutilized agents (threshold: <5 active)
- Reassignment recommendations

---

## Detection Queries

### Pattern 1 (Auth Vortex)
```python
blocked_keywords = ['notebooklm', 'auth', 'login', 'credential', 'ssh', 'oauth', 'token']
issues_blocked = [i for i in issues 
    if i.get('status') in ('blocked', 'in_progress')
    and any(k in i.get('title','').lower() for k in blocked_keywords)]
```

### Pattern 4 (Gap Ticketing)
```python
gap_tickets = [i for i in issues 
    if 'skill gap' in i.get('title','').lower()
    or 'establish skill' in i.get('description','').lower()]
```

### Pattern 5 (Hardware Block)
```python
hw_blocked = [i for i in issues
    if 'david at machine' in i.get('title','').lower()
    or 'blocked:' in i.get('title','').lower()
    or 'hardware' in i.get('description','').lower()]
```

---

## Velocity Calculation

```python
# Detect April 17 Anomaly (bulk update vs organic)
completions_by_day = Counter()
for i in done_issues:
    day = i.get('completedAt','')[:10]  # YYYY-MM-DD
    completions_by_day[day] += 1

# Organic = steady 5-10/day; Bulk = 100+ on single day
max_day = max(completions_by_day.values())
if max_day > 100:
    print(f"Bulk update detected: {max_day} on {max(completions_by_day, key=completions_by_day.get)}")
```

---

## Integration

Use with `paperclip-api` skill for data fetch, `discord` skill for notifications, `obsidian` skill for vault documentation.

**Output path:** `claude-vault/13-Reports/paperclip-fleet-audit-YYYY-MM-DD.md`
