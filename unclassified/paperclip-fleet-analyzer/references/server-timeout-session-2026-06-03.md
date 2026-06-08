# Server Timeout Session — 2026-06-03

## Context
Daily fleet-alignment cron audit. Paperclip REST API GET `/api/companies/{cid}/issues` timed out at every `limit` value (including `limit=5`). Agents endpoint also unresponsive. Required Postgres `json_agg` fallback.

## Observed
- **Issues:** 7,420 total issues
- **Agents:** 27 total agents
- **API behavior:** curl `--max-time 10` returned exit code 28 (timeout) for both agents and issues endpoints
- **Log file:** `server.log` was ~7.9MB (below the 50MB danger threshold)
- **Payload:** `json_agg` dump of issues table produced **28.6MB** of JSON
- **Root cause:** JSON payload serialization blocking the event loop — not log bloat, not route drift, not server crash

## Resolution
Used Postgres direct query via `json_agg` to extract both agents and issues tables:
```bash
psql -h 127.0.0.1 -p 54329 -U paperclip -d paperclip \
  -c "SELECT json_agg(row_to_json(t)) FROM (SELECT id, name, status, adapter_type, adapter_config, title, capabilities, reports_to, last_heartbeat_at FROM agents) t;" \
  > /tmp/agents_pg.json

psql -h 127.0.0.1 -p 54329 -U paperclip -d paperclip \
  -c "SELECT json_agg(row_to_json(t)) FROM (SELECT id, identifier, title, status, priority, assignee_agent_id, description FROM issues) t;" \
  > /tmp/issues_pg.json
```

**Parsing:** `find('[')` / `rfind(']')` to extract the JSON array from terminal-wrapped psql output.

## Schema Pitfall
`agents` table does **not** have a `reports_to_name` column. Only `reports_to` (UUID of parent agent). The skill inventory snippet referencing `reportsToName` fails if used against Postgres directly. Fixed in SKILL.md.

## Severity Impact
Fleet audit completed successfully via Postgres fallback, but the API being dead means **no agent can fetch work through the normal REST path**. If the fleet relies on API GET, this is a fleet-wide stall. The 5 `running` agents may have cached state or use alternate data paths.

## Key Takeaway
When GET times out but the server process is alive, test differential endpoints:
- Small endpoint (agents ~35KB) → fails = systemic (event loop or log bloat)
- Large endpoint (issues ~30MB) → fails alone = payload serialization

If log <10MB and small endpoint also fails, suspect event loop saturation from wake-up request spam or concurrent connections.
