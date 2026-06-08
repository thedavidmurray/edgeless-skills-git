# Gateway and API Provider Verification Cases

## Fireworks/Firepass Key Validation

Before rolling a new Fireworks firepass key across all configs:

```bash
# Test the key directly
curl -s https://api.fireworks.ai/inference/v1/chat/completions \
  -H "Authorization: Bearer fpk_YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "accounts/fireworks/routers/kimi-k2p6-turbo", "messages": [{"role": "user", "content": "Say pong"}], "max_tokens": 10}'
```

| Response | Meaning | Action |
|----------|---------|--------|
| `{"choices":...}` with assistant message | Key valid, working | Proceed with rollout |
| Rate limit (429) | Key valid, but throttled from concurrent gateway use | Key is good; wait for traffic to settle |
| 401 Unauthorized | Key invalid or expired | Do NOT rollout; get new key |
| 404 Path not found | `base_url` missing `/v1` suffix | Fix `base_url: https://api.fireworks.ai/inference/v1` |

## Discord Gateway Verification

Before claiming "all bots are online":

```bash
# Check launchd PIDs
launchctl list | grep hermes

# Check Discord connection in logs
for bot in hive beau kilo scribe edgeless-cc ombudsman trader; do
  echo "=== $bot ==="
  grep -E "Connected as|\u2713 discord connected" \
    ~/.hermes/profiles/$bot/logs/gateway.log 2>/dev/null | tail -2
done
```

**Verify each bot individually** — a PID in `launchctl` does NOT mean Discord is connected. Check the actual gateway log for:
- `[Discord] Connected as BotName#NNNN`
- `✓ discord connected`

**Trader/TBN special case:** Before claiming "Trader is connected", verify the token resolves correctly. If `DISCORD_BOT_TOKEN_PAMELA` was changed to `DISCORD_BOT_TOKEN`, check that the profile `.env` actually contains the expected token variable — do not assume the variable name in config.yaml matches the `.env` key.

## Vision Provider HTTP 426 Verification

When a bot gets stuck in an image-processing loop:

```bash
# Check the error
tail -5 ~/.hermes/profiles/<bot>/logs/gateway.error.log
```

If you see `HTTP 426: you must update Hermes Agent to access this free model`, the vision provider (likely Nous qwen) is on a deprecated free tier. Verify by checking the config:

```bash
grep -A5 "vision:" ~/.hermes/profiles/<bot>/config.yaml
```

If `provider: nous` and `model: qwen/qwen3.6-plus`, migrate to Fireworks K2.6.
