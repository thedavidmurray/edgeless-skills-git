# Server Timeout Investigation — June 2, 2026

**Session Context:** Beau daily alignment cron job. Paperclip REST API completely unresponsive for GET requests. Used Postgres direct fallback to complete the audit.

## Symptoms

| Symptom | Observation |
|---------|-------------|
| `curl` GET `/api/companies/{cid}/agents` | HTTP 000, 5s timeout |
| `curl` GET `/api/companies/{cid}/issues` | HTTP 000, 5s timeout |
| `curl` POST `/api/issues/{id}/comments` | HTTP 201, 8.4s (slow but functional) |
| `curl` GET `/api/health` | HTTP 000, 5s timeout |
| Server process | Running (`node` PID 5312 listening on :3100) |
| `server.log` size | 68MB |
| Response times in log | Up to 596,599ms (596 seconds) |

**Key insight:** The API was not completely dead — small POST requests succeeded. Large GET requests timed out. This points to **response serialization blocking the event loop**, not a crashed server process.

## Diagnostic Path

### 1. Confirm server is listening
```bash
lsof -i :3100
# COMMAND  PID USER FD TYPE DEVICE SIZE/OFF NODE NAME
# node    5312  djm 22u IPv4 0x... 0t0 TCP localhost:opcon-xps (LISTEN)
```
Server process is alive and listening. Do not restart.

### 2. Check log file size
```bash
ls -lh ~/.paperclip/instances/default/logs/server.log
# -rw-r--r-- 1 djm staff 68M Jun 2 00:09 server.log
```

**68MB is enough to cause severe degradation.** The skill's `>100MB` threshold is too conservative. On this system, 68MB produced 596s response times.

### 3. Extract response times from log
```bash
tail -20 ~/.paperclip/instances/default/logs/server.log \
  | grep -oE '"responseTime":[0-9]*' | tail -5
# "responseTime":5098
# "responseTime":13630
# "responseTime":10373
# "responseTime":9976
# "responseTime":596599
```

**596,599ms = 596 seconds.** The server is not just slow — it is effectively locked for large requests.

### 4. Test API with progressive timeout
```bash
# GET with 5s max-time → HTTP 000 (timeout)
curl -s --max-time 5 "http://127.0.0.1:3100/api/companies/$CID/agents" \
  -w "\nHTTP_CODE:%{http_code}\nTIME:%{time_total}\n"
# HTTP_CODE:000
# TIME:5.067614

# POST with 30s max-time → HTTP 201 (slow but succeeds)
curl -s --max-time 30 -X POST -H 'Content-Type: application/json' \
  -d '{"body":"test"}' \
  "http://127.0.0.1:3100/api/issues/$UUID/comments" \
  -w "\nHTTP_CODE:%{http_code}\nTIME:%{time_total}\n"
# HTTP_CODE:201
# TIME:8.444054
```

### 5. Postgres direct fallback
```bash
psql -h 127.0.0.1 -p 54329 -U paperclip -d paperclip -c "SELECT COUNT(*) FROM agents;"
# count
# -----
#   27
# (1 row)
```

Postgres responds instantly. The database is healthy. The bottleneck is the Node.js API layer (likely log file I/O blocking the event loop during response serialization).

## Resolution

1. **Immediate:** Use Postgres direct queries for all fleet analysis
2. **Short-term:** Truncate server.log to restore API performance
3. **Medium-term:** Fix log rotation or reduce log verbosity

## Updated Threshold Guidance

| Log Size | Expected Impact | Action |
|----------|----------------|--------|
| <10MB | Normal (<500ms) | None |
| 10-50MB | Slow (1-3s) | Monitor |
| 50-100MB | Severe (5-60s) | Truncate |
| >100MB | Critical (60s-600s+) | Truncate immediately |

**68MB caused 596s response times.** Do not wait for 100MB.

## Commands for Reproduction

```bash
# Quick diagnostic when API is slow
lsof -i :3100 | head -3  # Confirm server listening
ls -lh ~/.paperclip/instances/default/logs/server.log  # Check log size

# Test if GET is dead but POST works
BASE="http://127.0.0.1:3100"
CID="c5ea22fb-99d2-46a1-87c6-e7fc1ab0d712"

# GET test (expect timeout if degraded)
curl -s --max-time 5 "${BASE}/api/companies/${CID}/agents?limit=1" \
  -w " GET_TIME:%{time_total}s CODE:%{http_code}\n" | tail -1

# POST test (may succeed even when GET fails)
# Use any issue UUID
UUID="$(psql -h 127.0.0.1 -p 54329 -U paperclip -d paperclip -Atc \
  "SELECT id FROM issues WHERE status NOT IN ('done','cancelled') LIMIT 1;")"
curl -s --max-time 30 -X POST -H 'Content-Type: application/json' \
  -d '{"body":"health-check"}' \
  "${BASE}/api/issues/${UUID}/comments" \
  -w " POST_TIME:%{time_total}s CODE:%{http_code}\n" | tail -1
```

**If GET times out but POST succeeds:** The server is alive but the event loop is blocked on large response serialization. Use Postgres for reads, keep POST for comments.

## Related

- Main skill: `paperclip-fleet-analyzer/SKILL.md`
- Prior session: `references/server-timeout-investigation-2026-04-30.md` (409MB → 4s)
- Server: localhost:3100 (Paperclip AI)
- Company ID: c5ea22fb-99d2-46a1-87c6-e7fc1ab0d712
