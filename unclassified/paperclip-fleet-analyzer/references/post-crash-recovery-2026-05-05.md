# Post-Crash Recovery Log: 2026-05-05

## Incident: Unexpected Hard Shutdown

**Context:** System experienced hard shutdown. User requested swarm fleet verification on restart.

## Symptoms Detected

1. **Paperclip API completely down**
   - Port 3100 not listening
   - `curl: (7) Failed to connect`
   - Log file: 471MB (potential I/O slowdown cause)

2. **Discord Swarm partially degraded**
   - 6/7 bots running (hive, beau, edgeless-cc, scribe, ombudsman, trader, studio)
   - Missing: kilo (Codex execution bot)
   - All running gateways healthy

3. **Startup Failure Pattern**
   ```
   require() of ES Module /Users/djm/.npm/_npx/.../encoding-lite.js 
   from /.../html-encoding-sniffer.js not supported.
   Instead change the require of encoding-lite.js to a dynamic import()
   ```

## Root Cause

Node v20.11.0 + npx cached packages with ES Module/CommonJS incompatibility. 
Package `html-encoding-sniffer@latest` uses ESM but Paperclip's dependency 
chain expects CommonJS `require()`.

## Recovery Recipe

```bash
# 1. Truncate oversized log (optional but recommended)
cd ~/.paperclip/instances/default
tail -c 10M logs/server.log > /tmp/trimmed.log
mv /tmp/trimmed.log logs/server.log

# 2. Clear npx cache (CRITICAL for ES Module errors)
rm -rf ~/.npm/_npx/*/node_modules/html-encoding-sniffer
# OR full clear:
rm -rf ~/.npm/_npx/*

# 3. Retry with fresh package resolution
npx paperclipai@latest run --daemon

# 4. Verify
sleep 5
curl -s http://127.0.0.1:3100/api/health || echo "Still down"
lsof -i :3100
```

## Alternative: Node Version Pinning

If ES Module errors persist:

```bash
# Check available versions
nvm list

# Use Node 18 LTS (more stable with legacy CJS packages)
nvm use 18
npx paperclipai run --daemon
```

## Post-Recovery Validation Commands

```bash
# Full stack check
hermes status | grep -E "Gateway|Paperclip"
curl -s http://127.0.0.1:3100/api/companies/{cid}/agents | jq '. | length'
ps aux | grep "gateway run" | grep -v grep | wc -l
```

## Related Blockers After Hard Shutdown

- Nous Portal tokens expire ~24h after last refresh (check: `hermes status`)
- Discord gateways may need restart if Mac slept for >30min
- ChromaDB requires manual restart if not using launchd/background mode
- Kilo (Codex bot) needs explicit `hermes gateway run --profile kilo` if not auto-started

## References

- Node.js ESM/CJS interop: https://nodejs.org/api/esm.html#interoperability-with-commonjs
- Paperclip local_trusted mode: http://127.0.0.1:3100 (no auth required)
