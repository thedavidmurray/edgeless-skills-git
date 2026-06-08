# Paperclip Adapter Verification

Session: 2026-05-03 | Swarm Repair After Fireworks Restoration

## Context

After Fireworks account was restored following billing suspension, 5 Paperclip agents remained stuck in `error` status despite:
- Hermes gateways running fine locally with Fireworks/Kimi K2.5
- API keys valid (verified via curl)
- Discord bots connected and operational

Root cause: Paperclip adapter configs drifted from Hermes profile configs.

## Verification Pattern

When claiming "Paperclip agents fixed" or "configs aligned":

### 1. Query Paperclip API for actual adapter state

```bash
curl -s "http://127.0.0.1:3100/api/agents/{agent_id}" | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"{d['name']}: {d['status']} | adapter={d.get('adapterConfig',{}).get('provider')}/{d.get('adapterConfig',{}).get('model')}\")"
```

Expected vs actual sources of truth:
- **Paperclip adapterConfig** = stored in PostgreSQL, used for heartbeat runs
- **Hermes config.yaml** = local profile, used by gateway
- **Paperclip runtimeConfig** = can override adapterConfig (check for stale overrides)

### 2. Read Hermes Profile Config

```bash
cat ~/.hermes/profiles/{profile}/config.yaml | grep -A5 "^model:"
```

Look for:
```yaml
model:
  default: accounts/fireworks/models/kimi-k2p5
  provider: custom
  base_url: https://api.fireworks.ai/inference/v1
  api_key: ${FIREWORKS_API_KEY}
```

### 3. Verify Alignment

Create table comparing:

| Agent | Paperclip Provider | Paperclip Model | Hermes Provider | Hermes Model | Aligned? |
|-------|-------------------|-----------------|-----------------|--------------|----------|
| Beau | openai-codex | gpt-5.3-codex | custom | fireworks-kimi | ✗ |
| Scribe | openrouter | owl-alpha | custom | fireworks-kimi | ✗ |

### 4. Post-Update Verification

After PATCH to update adapterConfig:

```bash
# Immediate: Check API response
result=$(curl -s -X PATCH "..." -d '{...}')
echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"Updated: {d.get('adapterConfig',{}).get('provider')}\")"

# Verify: Re-query to confirm persisted
curl -s "http://127.0.0.1:3100/api/agents/{agent_id}" | \
  python3 -c "import sys,json; d=json.load(sys.stdin); 
    expected_provider='custom'
    actual_provider=d.get('adapterConfig',{}).get('provider')
    print(f\"✓ Verified\" if actual_provider==expected_provider else f\"✗ Mismatch: expected {expected_provider}, got {actual_provider}\")"
```

### 5. Set Status to Idle

After config update, must explicitly set status:

```bash
curl -s -X PATCH "http://127.0.0.1:3100/api/agents/{agent_id}" \
  -d '{"status": "idle"}' | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"Status: {d.get('status')}\")"
```

Without this, agent remains in `error` state even with correct adapter.

## Common Pitfalls

1. **Checking only gateway process** — process running ≠ Paperclip can communicate with it
2. **Assuming config.yaml updates propagate** — Paperclip has its own database, doesn't read Hermes configs
3. **Forgetting runtimeConfig overrides** — runtime can shadow adapterConfig, causing confusion
4. **Not verifying after PATCH** — API may return 200 but not persist if malformed
5. **Reporting before status=idle** — adapter fixed but agent still marked error until status changed

## Session Outcome

Applied to 5 agents (Beau, Scribe, Cypher, Hive, Edgeless CC):
- All adapters migrated to `custom/fireworks-kimi-k2p5` (except Edgeless CC staying on Nous)
- All status set to `idle`
- Verification: Re-queried each agent, confirmed provider/model alignment

Edge case: Edgeless CC on Nous required separate auth flow (not config mismatch).
