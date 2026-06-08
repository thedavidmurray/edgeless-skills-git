# Phantom Migration Incident — May 16-17, 2026

## Incident Summary

On May 16, 2026, a session claimed to have migrated 18 Hermes profiles from Fireworks to Groq due to perceived Fireworks auth failure (403/NOT_FOUND). On May 17, a subsequent session discovered that **14+ of those profiles were still on Fireworks** — the migration had never actually been applied to most configs despite being "shipped."

This is a **phantom migration**: a claimed bulk config change that appears in session transcripts and memory but was never persisted to the actual filesystem.

## Root Causes

1. **Confabulated completion:** The agent claimed success without verifying that files were actually written
2. **Silent failures:** The migration script may have run but returned partial success that was not reported
3. **External reversion:** Another process (cron job, gateway restart, config sync) may have reverted the changes
4. **Wrong target:** The script may have modified the wrong paths (e.g., `~/.hermes/config.yaml` but not `~/.hermes/profiles/*/config.yaml`)

## Detection Pattern

After any claimed mass migration, ALWAYS run:

```bash
# Check which profiles still have the OLD provider
grep -rl 'api.fireworks.ai' ~/.hermes/profiles/*/config.yaml 2>/dev/null | \
  while read f; do echo "STILL ON OLD: $(basename $(dirname $f))"; done

# Check which profiles have the NEW provider
grep -rl 'api.groq.com' ~/.hermes/profiles/*/config.yaml 2>/dev/null | \
  while read f; do echo "ON NEW: $(basename $(dirname $f))"; done
```

If the "STILL ON OLD" list is non-empty, the migration was phantom.

## Verification Checklist

- [ ] Run `grep` across ALL profile configs for old provider
- [ ] Check global `~/.hermes/config.yaml` for old provider
- [ ] Check `fallback_model` blocks in ALL configs for old provider
- [ ] Verify backup directory exists and contains original configs
- [ ] Run `hermes profile show <name>` on a few random profiles to confirm runtime reality
- [ ] If ANY profile still has old provider, re-run migration before proceeding

## Prevention

1. **Verify before claiming:** After `write_file` or sed on config files, `read_file` the result back
2. **Use atomic operations:** Write to temp file, verify, then `mv` into place
3. **Backup first:** Always preserve `.bak` files so you can compare
4. **Audit after:** Run the grep verification as the FINAL step of any migration task

## Session Details

- **May 16 session:** Claimed migration of 18 profiles from Fireworks → Groq
- **May 17 discovery:** `grep -rl 'api.fireworks.ai' ~/.hermes/profiles/*/config.yaml` returned 16 profiles still on Fireworks
- **Actual working provider:** Fireworks FirePass was LIVE with correct model path `accounts/fireworks/routers/kimi-k2p6-turbo`. The May 16 "403" diagnosis was wrong.
- **Correct fix:** Migrated all 23 profiles back to Fireworks with correct path, patched NameError in `conversation_loop.py`, restarted gateways
- **Verification command used:** `grep -A6 '^model:' ~/.hermes/profiles/{name}/config.yaml | head -7`

## Related

- `swarm-coordination/references/fleet-auth-cascade-recovery.md` — full recovery protocol with corrected provider matrix
- `hermes-agent/SKILL.md` — `_pool_may_recover_from_rate_limit` NameError fix
