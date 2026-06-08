# Agent Error Diagnosis — Session Log 2026-05-17

Session finding: 9+ agents showing `error` or degraded status simultaneously. Root cause was NOT a code bug, infrastructure failure, or Paperclip crash — it was a **provider-side Fireworks/Kimi K2.6 quota collapse** hitting every agent configured with that model.

---

## Diagnosis Timeline

### Step 1: Surface Check — Paperclip Status
```
Agent          Status    Heartbeat
Edgeless CC    error     2026-05-17 13:22
Kilo           error     2026-05-17 13:12
Beau           running   2026-05-17 13:22  ← actually dead, status hadn't flipped
Scribe         running   2026-05-17 13:22  ← degraded but not flipped
Anomaly        idle      2026-05-17 19:27  ← 100% failure rate, still idle
```

**Key insight:** Paperclip status is lagging. `running` and `idle` do NOT mean healthy.

### Step 2: REST API Failure
```bash
curl -s --max-time 15 "http://127.0.0.1:3100/api/companies/{cid}/issues?limit=5"
# HTTP_CODE:000  TIME:15.003s
```
The Paperclip REST API was completely hung on issue queries. Had to fall back to embedded Postgres.

### Step 3: Postgres Direct Query — Evidence Gathering
```python
import psycopg2
conn = psycopg2.connect(host='127.0.0.1', port=54329, database='paperclip', user='paperclip')
```

**Heartbeat run failure rate (last 6 hours):**
| Agent | Failed | Succeeded | Timed Out |
|-------|--------|-----------|-----------|
| Beau | 183 | 52 | 16 |
| Edgeless CC | 156 | 19 | 26 |
| Scribe | 44 | 8 | 9 |
| Anomaly | 54 | 0 | 1 |
| Kilo | 24 | 4 | 4 |

### Step 4: ndjson Run-Log Analysis — Root Cause Found

File: `~/.paperclip/instances/default/data/run-logs/{cid}/{agent_id}/{run_id}.ndjson`

Every failing agent's stdout chunk contained:
```
API call failed after 8 retries: HTTP 429: The usage limit has been reached
```

**Sample ndjson structure:**
```json
{"ts":"2026-05-17T20:22:44.825Z","stream":"stdout","chunk":"[paperclip] No project or prior session workspace was available..."}
{"ts":"2026-05-17T20:28:31.305Z","stream":"stderr","chunk":"\nsession_id: 20260517_132253_e82877\n"}
{"ts":"2026-05-17T20:28:31.308Z","stream":"stdout","chunk":"API call failed after 8 retries: HTTP 429: The usage limit has been reached\n"}
```

### Step 5: Cross-Agent Model Comparison

**Agents NOT affected** (alternate models/providers):
| Agent | Model | Provider | Status |
|-------|-------|----------|--------|
| Curator | qwen/qwen3.6-plus | nous | idle (healthy) |
| Gemini Scout | gemini-2.5-flash | custom | idle (healthy) |
| Groq Scout | llama-3.1-8b-instant | groq | idle (healthy) |
| Groq Reasoner | deepseek-r1-distill-llama-70b | groq | idle (healthy) |
| Cerebras Scout | llama-3.3-70b | cerebras | idle (healthy) |
| Editor | accounts/fireworks/routers/kimi-k2p5-turbo | custom | idle (healthy) |

**All affected agents** were on:
```
model: accounts/fireworks/routers/kimi-k2p6-turbo
provider: custom (Fireworks)
```

### Step 6: Secondary Failure — Anthropic Credit Exhaustion

| Agent | Adapter | Error |
|-------|---------|-------|
| CEO | claude_local | `Claude run failed: Credit balance is too low` |

Separate provider, same pattern: provider-side quota/credit exhaustion.

### Step 7: Config Drift Discovery — Kilo on Wrong Model

Kilo's Paperclip `adapter_config`:
```json
{
  "model": "accounts/fireworks/routers/kimi-k2p6-turbo",
  "provider": "custom"
}
```

**Problem:** Kilo is the Codex execution specialist. He should be on `o4-mini` or `gpt-5.3-codex` (OpenAI), not Kimi K2.6 (Fireworks). He's burning coordinator-grade quota while also failing to do his actual job.

---

## Verification Queries

### Count runs by status per agent (last 6 hours)
```sql
SELECT a.name, h.status, COUNT(*)
FROM heartbeat_runs h
JOIN agents a ON h.agent_id = a.id
WHERE h.started_at > NOW() - INTERVAL '6 hours'
GROUP BY a.name, h.status
ORDER BY a.name, h.status;
```

### Get full adapter config for all agents
```sql
SELECT name, adapter_type, adapter_config
FROM agents
ORDER BY name;
```

Note: `adapter_config` is stored as JSONB. In Python with psycopg2 it returns as a dict; cast to text if querying via CLI.

### Find all ndjson log files for an agent in last 2 hours
```bash
CID="c5ea22fb-99d2-46a1-87c6-e7fc1ab0d712"
AGENT_ID="575260e2-9c2b-4c1d-abc6-1fff98c7abf1"  # Beau
find ~/.paperclip/instances/default/data/run-logs/${CID}/${AGENT_ID}/ \
  -name "*.ndjson" -mmin -120 | sort | tail -5
```

### Extract error lines from ndjson (jq one-liner)
```bash
cat *.ndjson | jq -r 'select(.stream == "stdout" and .chunk | contains("429")) | .chunk'
```

---

## Recovery Actions Taken / Recommended

1. **Immediate:** Check Fireworks dashboard for quota/billing — top up or switch mass agents to alternate provider (Nous, Groq, OpenRouter)

2. **Kilo:** Fix adapter_config to use his designated Codex/OpenAI model instead of Kimi. This is a double fix: frees up Fireworks quota AND restores his execution capability.

3. **CEO:** Add Anthropic credits or switch to OpenRouter-backed Claude.

4. **Beau:** Pause his "Recover stalled issue" cron loop until quota is restored. 183 failed runs in 6 hours means he's spamming the API and making the problem worse.

5. **Status flip lag:** Manually PATCH affected agents to `error` if they're still showing `idle`/`running` but have 100% failure rate, so Paperclip's scheduler stops assigning them work.

---

## Key Lesson

**"Adapter failed" is never the root cause.** It is Paperclip's generic wrapper around whatever Hermes emitted. The actual error is always in the ndjson run-log stdout. The diagnosis chain is:

1. Check `agents.status` → gives you suspects
2. Query `heartbeat_runs` → gives you failure rate and last error text
3. Read `.ndjson` run logs → gives you the real Hermes error
4. Compare across agents → tells you if it's systemic (all same model) or isolated
5. Check `agents.adapter_config` → catches config drift (wrong model assigned)
