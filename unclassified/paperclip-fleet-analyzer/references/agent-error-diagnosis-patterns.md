# Agent Error State Diagnosis Patterns

## The "Stale Error" Problem

Agents showing `status: error` in Paperclip may have residual error state from a terminated run rather than an actively failing agent.

### Diagnosis Flow

```python
import urllib.request, json

company = "c5ea22fb-99d2-46a1-87c6-e7fc1ab0d712"
agent_name = "Critic"

# 1. Get all agents
url = f"http://127.0.0.1:3100/api/companies/{company}/agents"
resp = urllib.request.urlopen(url)
agents = json.loads(resp.read())

# 2. Find target agent
target = [a for a in agents if a.get("name") == agent_name]
if not target:
    print(f"Agent '{agent_name}' not found")
    exit()

a = target[0]
print(f"Name: {a['name']}")
print(f"Status: {a['status']}")
print(f"Last heartbeat: {a.get('lastHeartbeatAt', 'never')}")

# 3. Determine if error is stale
from datetime import datetime, timezone
hb = a.get("lastHeartbeatAt")
if hb:
    dt = datetime.fromisoformat(hb.replace("Z", "+00:00"))
    age = (datetime.now(timezone.utc) - dt).total_seconds()
    hours_ago = age / 3600
    print(f"Age: {hours_ago:.1f}h ago")
    
    if hours_ago > 2 and a["status"] == "error":
        print("→ LIKELY STALE ERROR. Agent terminated, state never cleared.")
        print("  Residual error — check workspace for crash logs.")
    elif hours_ago < 0.25 and a["status"] == "error":
        print("→ FRESH ERROR. Agent likely actively failing.")
        print("  Check adapter config (provider, model, apiKey).")
    else:
        print(f"→ Borderline. Age={hours_ago:.1f}h. Manual review advised.")
```

### API Endpoint Quirk

```
/agents/{id}              → 404 (doesn't exist)
/agents?agentId={id}      → works, returns list filtered by ID
```

**Workaround:** Fetch full `GET /companies/{id}/agents` and filter in Python.

## Real Example (2026-04-30 Critic)

- **Status:** `error`
- **Last heartbeat:** 2026-04-30 21:53 UTC
- **Checked at:** 2026-05-01 08:40 UTC (~11h stale)
- **Verdict:** Stale error — Critic's last run (EDGA-892, verify-before-claiming chroma sanity-check) finished/terminated but status never reset to `idle`.
- **Adapter config:** hermes_local, Kimi K2.5 (Fireworks), 600s timeout, cwd=pen-plotter-art

### What to Do About Stale Errors

1. **If agent has pending work:** Force a new execution — Paperclip may clear error state on next heartbeat
2. **If agent is idle:** Consider PATCH-ing the agent status to `idle`:
   ```bash
   curl -s -X PATCH "http://127.0.0.1:3100/api/agents/$AGENT_ID" \
     -H "Content-Type: application/json" \
     -d '{"status": "idle"}'
   ```
3. **If error persists after status update:** Check `adapterConfig` for stale `provider: "auto"` (should be explicit like `fireworks`)

## Endpoint: Agent Detail by Query Param

Found that `/api/companies/{companyId}/agents/{agentId}` returns **404 Not Found**.

The correct pattern:
```python
url = f"http://127.0.0.1:3100/api/companies/{company}/agents?agentId={agent_id}"
resp = urllib.request.urlopen(url)
data = json.loads(resp.read())  # Returns a list (filtered)
```

This returns an array containing just that agent (if found) or an empty array. Example structure:
```json
[
  {
    "id": "7898e3ea-73de-4057-89ab-f0f932d7e990",
    "name": "Critic",
    "status": "error",
    "lastHeartbeatAt": "2026-04-30T21:53:39.393Z",
    "adapterType": "hermes_local",
    "adapterConfig": {
      "provider": "fireworks",
      "model": "accounts/fireworks/models/kimi-k2p5",
      "cwd": "/Users/djm/claude-projects/pen-plotter-art",
      "timeoutSec": 600
    }
  }
]
```
