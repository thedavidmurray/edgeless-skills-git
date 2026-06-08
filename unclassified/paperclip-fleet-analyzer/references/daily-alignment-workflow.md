# Daily Alignment Report Workflow

End-to-end operational health check for a Paperclip-managed agent fleet, combining fleet status, backlog analysis, cron health, auth probes, and blocked-work triage into a single deliverable report.

## When to Use

- **Beau/VPS cron job** — Run every 24h as the source-of-truth intake operator
- **Post-crash recovery validation** — Confirm fleet is healthy after restarts
- **Pre-weekend board cleanup** — Identify what will stall over the weekend
- **Provider incident follow-up** — Verify auth cascade is resolved before declaring all-clear

## Workflow

### Phase 1: Fleet Snapshot

```bash
# Agents: status, adapter, model
curl -s "http://127.0.0.1:3100/api/companies/{cid}/agents" | jq -r '.[] | [.name, .status, .adapterType, .adapterConfig.model] | @tsv'

# Key metric: count by status
# Expected: mostly idle, some running, minimal error
```

**Red flags:**
- `error` agents with recent heartbeat but zero execution progress
- `idle` agents that have 0 assigned work despite open backlog
- Adapter/model drift (e.g., `kimi-k2p5-turbo` when fleet migrated to `k2p6-turbo`)

### Phase 2: Backlog Enumeration (Status-Specific)

```bash
# Query EACH status separately — the API returns accurate buckets when filtered
for s in todo backlog in_progress blocked; do
  curl -s "http://127.0.0.1:3100/api/companies/{cid}/issues?limit=100&status=$s" -o /tmp/issues_$s.json
done
```

**Never rely on a single `limit=250` unfiltered query** for alive-count reporting. The API returns all statuses mixed together; unfiltered counts are meaningless.

**Key metrics:**
- `todo` count (ready to claim)
- `backlog` count (needs grooming)
- `in_progress` count (active work)
- `blocked` count (needs unblock)
- `unassigned` in todo/backlog (routing gap)
- `originKind == 'stranded_issue_recovery'` (noise)

### Phase 3: Agent-Specific Deep-Diagnosis (Error Agents)

When an agent shows `error`, do not stop at the status field. Follow the evidence chain:

| Layer | Probe | What it tells you |
|-------|-------|-------------------|
| Surface | `agents.status` | `error`, `running`, `idle` |
| Run logs | `~/.paperclip/.../run-logs/{cid}/{agent_id}/*.ndjson` | Full Hermes stdout/stderr |
| Gateway | `~/.hermes/profiles/{profile}/logs/gateway.log` | Platform connection health |
| Cron | `hermes cron list` | Whether the agent's scheduled jobs are failing |
| Auth | `claude-projects/logs/auth-health-YYYYMMDD.json` | Provider health snapshot |

**Cascading provider failure signature:**
```
1.6KB run log → "API call failed after N retries: HTTP 429"
Primary provider (e.g., Fireworks) → HTTP 403 auth_error
Fallback provider (e.g., Gemini) → HTTP 429 free-tier quota exhausted (limit: 0)
```

**Action:** Check auth health log for cross-provider confirmation. If multiple agents on the same model fail simultaneously while agents on alternate models stay healthy, it's a provider quota collapse.

### Phase 4: Cron Health Audit

```bash
hermes cron list 2>&1
```

**TUI output truncation risk:** `hermes cron list` renders a table that can truncate long rows. For programmatic parsing, use the raw output and grep for:
- `error:` (any job with a non-ok last run)
- `Script not found:` (path drift)
- `Discord API error (401)` (expired delivery tokens)
- `Next run:  ?` (schedule parse failure or broken repeat)

**Critical cron failures to flag:**
| Pattern | Meaning |
|---------|---------|
| `HTTP 429: The usage limit has been reached` | Provider quota hit during cron execution |
| `Script exited with code 2` | Auth probe or health script detected critical degradation |
| `Script not found:` | Path changed; cron still references old location |
| `Discord API error (401)` | Bot token expired; no alerts will reach Discord |

### Phase 5: Build the Report

**Standard sections:**
1. **Fleet Status** — agent counts by status, error agents named
2. **Backlog State** — todo/backlog/blocked/in_progress counts, recovery noise count
3. **Agent Operational Status** — For the agent running this workflow (Beau): status, last heartbeat, root cause, impact
4. **Cron Health** — Table of jobs with failures highlighted
5. **Blocked Work** — Issues requiring VPS/ops attention with blocker type
6. **Recommendations** — Immediate / short-term / strategic

### Phase 6: Deliver

**Two-channel delivery:**
1. **Paperclip comments** — Post summary to the most relevant open issue (e.g., cron P0 or the agent's own blocked issue)
   ```bash
   curl -s -X POST -H 'Content-Type: application/json' \
     -d '{"body": "..."}' \
     "http://127.0.0.1:3100/api/issues/{uuid}/comments"
   ```
   - Returns 201 on success
   - Returns 500 on terminal-state issues (done/cancelled) — skip those

2. **Vault write** — Save full report to `claude-vault/13-Reports/daily-alignment/YYYY-MM-DD-{agent}-daily-alignment.md`

**Never deliver only to Discord** — Discord tokens expire; Paperclip comments and vault files are the durable record.

## Session-Specific Artifacts

- 2026-05-27 report (Beau, cascading auth failure): `claude-vault/13-Reports/daily-alignment/2026-05-27-beau-daily-alignment.md`
- Auth health log referenced: `claude-projects/logs/auth-health-20260527.json`
- Paperclip comments posted to: EDGA-5903, EDGA-5892
