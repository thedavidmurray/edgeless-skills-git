# Session Findings — 2026-06-04

## API Degradation Pattern

**Observation:** Paperclip REST API completely unresponsive to bulk reads during daily audit.

- `GET /api/companies/{cid}/agents` → HTTP 000, 5s timeout
- `GET /api/companies/{cid}/issues?limit=500` → HTTP 000, 5s timeout
- Individual `GET /api/issues/{id}` → 16-28s response times (200 OK but extremely slow)
- Small paginated `GET /issues?limit=5&offset=55` → 16-19s response times

**Postgres fallback:** Worked perfectly. `json_agg` extracted 7,975 issues and 27 agents in ~5 seconds.

## Server State

| Metric | Value |
|--------|-------|
| server.log | 2.8MB |
| Total logs directory | 85MB |
| Node process | Running (PID 55026) |
| Postgres processes | 10+ concurrent SELECT queries |
| Response times (server.log) | 16,240ms - 28,255ms for individual issue endpoints |

**Note:** Server.log is only 2.8MB, far below the 50MB "severe" threshold. Response times were 20-30s anyway. This suggests **database query pressure** from 7,975 issues + concurrent agent polling, not purely log bloat. The existing log-size threshold table should be supplemented with DB-size awareness when issue counts exceed ~7,000.

## Fleet State

| Status | Count |
|--------|-------|
| running | 5 (Anomaly, Curator, Beau, Studio 2, Edgeless CC) |
| idle | 3 (Critic, Minter, pamela) |
| paused | 13 (Builder, Cypher, Kilo, Scribe, Verifier, Specimen, Trader, NGA-Scout, Ombudsman, Claude, Editor, Hive, Cerebras Scout) |
| error | 1 (CEO) |
| pending_approval | 1 (Engineer) |
| terminated | 4 (Envoy, Hermes, Pamela, Trader 2) |

## Critical Finding: Paused Agent Stalled Work

13 paused agents collectively hold **170 active issues**:

| Agent | Status | Active Issues |
|-------|--------|--------------|
| Scribe | paused | 100 |
| Builder | paused | 21 |
| Trader | paused | 11 |
| Cypher | paused | 10 |
| Kilo | paused | 9 |
| Minter | idle | 9 |
| Specimen | paused | 6 |
| Verifier | paused | 5 |
| NGA-Scout | paused | 3 |
| Hive | paused | 3 |

This is distinct from orphaned issues (0 found). The agents exist but are not polling. Work is effectively frozen.

## Other Metrics

| Metric | Value |
|--------|-------|
| Total issues | 7,975 |
| Active issues | 1,463 |
| Unassigned active | 941 |
| High/critical unassigned | 45 |
| Blocked-work matches | 529 |
| Orphaned (dead agents) | 0 |

## Skill Gaps Detected

| Skill | Count in backlog |
|-------|-----------------|
| mcp_builder | 226 |
| generative_art | 174 |
| youtube_pipeline | 158 |
| vector_db | 79 |
| cron_automation | 69 |
| trading_automation | 37 |
| messaging | 29 |

## Analysis Technique

This session used **pure `jq` shell analysis** instead of Python heredocs for all counting, grouping, and filtering. The `jq` approach was faster and more reliable in a cron context where Python script execution requires approval.

Example patterns:
```bash
# Parse Postgres json_agg output via sed + jq
sed -n '/\[.*\]/p' /tmp/issues_pg.json > /tmp/issues_clean.json
jq 'length' /tmp/issues_clean.json

# Group by status
jq -r 'group_by(.status)[] | "\(.[0].status): \(. | length)"' /tmp/issues_clean.json

# Filter active issues, extract fields
jq -r '.[] | select(.status != "done" and .status != "cancelled") | [.identifier, .status, .title] | @tsv'
```

## Action Taken

- Reported RED severity to Discord `#audit-log`
- Wrote durable artifact to `claude-vault/13-Reports/daily-alignment/2026-06-04-fleet-daily.md`
- No Paperclip issues auto-created (per daily run policy: recommendations only)

## Root Cause Hypothesis

The 13 paused agents likely paused because their API calls (listing assigned issues) timed out, causing gateway to detect failure and pause. The server is under query pressure from 7,975 issues and many concurrent agents. The API GET path is effectively blocked by large JSON serialization, while the Postgres direct path is unaffected because it bypasses the Node.js event loop entirely.
