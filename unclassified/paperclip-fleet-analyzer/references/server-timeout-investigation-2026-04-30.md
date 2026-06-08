# Server Timeout Investigation — April 30, 2026

**Session Context:** User reported "still getting a lot of timeouts" when interacting with Paperclip agents.

## Investigation Steps

### 1. Check Log File Size

```bash
ls -lh ~/.paperclip/instances/default/logs/server.log
# Result: 409M (409 MB)
# Impact: Excessive disk I/O, response times degraded from ~200ms to 4s+
```

**Finding:** 409MB log file — rotation likely broken or logs never truncated.

### 2. Analyze Response Time Distribution

```bash
tail -1000 ~/.paperclip/instances/default/logs/server.log \
  | grep -o '"responseTime":[0-9]*' \
  | sed 's/"responseTime"://' \
  | sort -n | tail -20
```

**Results:**
```
1745
1754
1777
...
3510
3799
4123  ← Maximum: 4.1 seconds
```

**Thresholds identified:**
- Normal: <500ms
- Slow: 1-2s (occasional)
- Critical: >3s (timeouts happening)

### 3. Check Concurrent Agent Processes

```bash
ps aux | grep -c "hermes.*chat.*-q"
# Result: 4 concurrent hermes chat processes

ps aux | grep "hermes chat" | wc -l
# Result: 2 (after filtering)
```

**Finding:** Not excessive contention — issue is server-side (log size), not agent-side.

### 4. Paperclip Server Process Health

```bash
ps aux | grep -E "node.*paperclip|56874"
# PID 56874: node paperclipai run (main server)
# PID 38159: postgres paperclip (DB connection)

lsof -i :3100 | head -20
# Multiple established connections from browser UI polling
```

**Finding:** Server healthy, but handling excessive polling from browser UI.

---

## Root Cause Analysis

| Factor | Finding | Impact |
|--------|---------|--------|
| Log file size | 409 MB | 🔴 HIGH — disk I/O bottleneck |
| Response times | Up to 4.1s | 🔴 HIGH — user timeouts |
| Concurrent agents | 2-4 active | 🟡 MEDIUM — normal load |
| UI polling | 7+ req/sec | 🟡 MEDIUM — unnecessary load |

**Primary cause:** Log file bloat causing disk write delays → response time spikes.

**Contributing:** Browser UI polling `/live-runs` and `/issues` endpoints continuously.

---

## Fleet Status Discovered

**Total agents:** 20

### Status Breakdown

| Status | Count | Agents |
|--------|-------|--------|
| idle | 17 | Most of fleet |
| running | 2 | Hive, Minter |
| error | 1 | Scribe (later found stale) |

### Key Findings

| Agent | Status | Notes |
|-------|--------|-------|
| Builder | error → idle | Reset required |
| Scribe | error → idle | Reset required |
| Critic | idle | Ready for pen-plotter scoring work |
| Edgeless CC | idle | Ready for iOS app review |
| Kilo | idle | Ready for fast-track protocol |
| Ombudsman | idle | Ready for triage pipeline audit |
| Verifier | idle | Ready for QA backlog |

---

## Resolution Actions

1. **Immediate:** Truncate 409MB server.log to restore performance
2. **Short-term:** Reduce browser UI polling frequency
3. **Medium-term:** Fix log rotation or implement size-based truncation
4. **Agent resets:** Transition Builder, Scribe from error → idle → running
5. **Task assignments:** Match idle agents to open work (see Task Assignment section)

---

## Commands for Future Investigations

### Quick Timeout Diagnosis

```bash
# 1. Check log size (primary suspect)
ls -lh ~/.paperclip/instances/default/logs/server.log

# 2. Get response time distribution
tail -1000 ~/.paperclip/instances/default/logs/server.log 2>/dev/null \
  | grep -o '"responseTime":[0-9]*' \
  | sed 's/"responseTime"://' \
  | sort -n | tail -20

# 3. Count slow responses (>1s)
tail -5000 ~/.paperclip/instances/default/logs/server.log 2>/dev/null \
  | grep -c '"responseTime":[1-9][0-9][0-9][0-9]'

# 4. Check concurrent agents
ps aux | grep -c "hermes.*chat"

# 5. Full fleet status
curl -s "http://127.0.0.1:3100/api/companies/{COMPANY_ID}/agents" \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Total: {len(data)}')
for a in data:
    print(f\"{a.get('name','?'):12} | {a.get('status','?'):8} | {a.get('adapterType','?'):15}\")
"
```

### Truncate Oversized Log

```bash
# Preserve last 10MB, truncate rest
tail -c 10M ~/.paperclip/instances/default/logs/server.log > /tmp/server.log.tmp
mv /tmp/server.log.tmp ~/.paperclip/instances/default/logs/server.log

# Or simply rotate
mv ~/.paperclip/instances/default/logs/server.log \
   ~/.paperclip/instances/default/logs/server.log.old
# Server will create new log on next write
```

---

## Related Files

- Main skill: `paperclip-fleet-analyzer/SKILL.md`
- Session context: User requested timeout audit after budget changes
- Server: localhost:3100 (Paperclip AI)
- Company ID: c5ea22fb-99d2-46a1-87c6-e7fc1ab0d712
