# Discord Bot Swarm Audit Pattern (2026-05-01)

Use this reference when analyzing a Paperclip-managed Discord bot swarm that is noisy, silent, looping, over-budget, or confusing.

## Core lesson

A bot swarm can look like a Discord prompt problem while the actual root cause is cross-layer drift:

1. Paperclip agent intent differs from Hermes profile runtime.
2. Hermes cron jobs fail due to provider budget/auth while gateways remain connected.
3. Cron/scripts post Discord messages directly, bypassing bot identity rules.
4. Envelope identity (`[FROM:Hive]`) differs from platform author identity.
5. Dispatchers post `[TYPE:ASSIGNED]` without mutating Paperclip state, causing repeated fake assignments.
6. Anti-loop rules prevent useful coordination but do not dedupe script-generated spam.
7. Humans and agents lack a canonical capability/routing map.

## Audit sequence

1. Fetch Paperclip agents/issues through localhost API and save JSON before parsing.
2. Compare Paperclip intent (`adapterType`, `adapterConfig.provider/model`) with Hermes runtime (`~/.hermes/profiles/<agent>/config.yaml`).
3. Check `hermes cron list` and profile cron JSON for provider budget/auth failures.
4. Check gateway/process state separately; connected gateway does not mean agent work succeeds.
5. Read recent #general and #bot-backroom messages with `discli`.
6. Search profile scripts for direct Discord posting: `discord.com/api/v10/channels`, `discli msg send`, webhook scripts, hardcoded channel IDs.
7. Verify platform author identity matches `[FROM:*]` in message envelopes.
8. Verify dispatchers mutate source-of-truth state. If a script posts `[TYPE:ASSIGNED]`, it must call Paperclip checkout/PATCH and re-GET the issue to confirm `assigneeAgentId` changed.
9. Check profile `channel_directory.json` after migrations; Telegram/Discord targets must exist under the migrated profile, not just another profile or old VPS.

## Bot-to-bot state machine

Use this instead of blanket silence or free chatter:

`ROUTE -> ACK -> (QUESTION -> ANSWER)* -> COMPLETE|BLOCKED`

Allowed acts:

1. ROUTE
2. ACK
3. QUESTION
4. ANSWER
5. COMPLETE
6. BLOCKED
7. STATUS

Forbidden acts:

1. ACK of ACK
2. ACK of COMPLETE
3. ACK of STATUS
4. Signoff/standby-only messages
5. Unaddressed bot replies in #general

Dedupe key: `FROM + TO + TYPE + REF`, with a TTL such as 6 hours.

## Configuration pitfalls

- Only one coordinator should have free response in #general.
- Non-coordinator bots should be mention-only in #general.
- #bot-backroom should use addressed envelopes, not broad free response.
- `discord:` must be top-level in Hermes config; nested `persona.discord` is likely ignored.
- OpenAI OAuth/OpenAI Codex profiles should not keep stale `api_key`, `base_url`, or incompatible `api_mode` under `model:`.
- A Paperclip `codex_local` agent should not have Hermes runtime still set to `openrouter` unless that is intentional.

## Capability registry pattern

Create both:

1. Human-readable: `claude-vault/02-Agents/swarm-capability-registry.md`
2. Machine-readable: `config/swarm-capabilities.yaml`

Minimum fields: agent_name, discord_handle, paperclip_agent_id, model_provider, model_name, cost_tier, gateway_host, channels, listens_to, ignores, capabilities, prohibited_tasks, escalation_path, current_status_source.
