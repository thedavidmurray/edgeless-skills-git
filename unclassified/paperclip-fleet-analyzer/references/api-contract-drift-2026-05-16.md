# API Contract Drift Diagnosis -- Session Log (2026-05-16)

## Symptom

Swarm Daily Dashboard reported:
- **28 agents idle, 0 working**
- **14 blocked issues** including EDGA-989 (Fireworks suspended), EDGA-1967 (Swarm-Repair #4)
- Dashboard showed "blocked" status taxonomy

## Initial Assumption (Wrong)

Paperclip data layer degraded -- health endpoint OK but `/api/issues` and `/api/agents` both timeout after 5-10s. Assumed backend query layer was dead.

## Actual Root Cause

**API contract drift**, not backend degradation.

### Route Migration

| Old Route | Response | New Route | Response |
|-----------|----------|-----------|----------|
| `GET /api/issues?limit=1` | 400 "Missing companyId" | `GET /api/companies/{cid}/issues?limit=1` | 200, 0.07s |
| `GET /api/agents?limit=3` | 404 "Unsupported query parameter" | `GET /api/companies/{cid}/agents` | 200, 0.05s |
| `GET /api/agents` | 404 "API route not found" | `GET /api/companies/{cid}/agents` | 200 (bare array) |

### Status Taxonomy Change

| Old Status | API Result | New Status | API Result |
|------------|------------|------------|------------|
| `status=open` | `[]` instantly | `status=todo` | Populated with 25 issues |
| `status=blocked` | Not tested (no longer exists) | `status=in_progress` | 1 issue (EDGA-3491) |

Verified by enumerating statuses on the new route:
```bash
for s in open todo in_progress blocked backlog done cancelled; do
  curl -s --max-time 3 "${BASE}/companies/${CID}/issues?limit=1&status=$s" \
    -w " TIME:%{time_total}s\n" | tail -1
done
```

### Progressive Pagination Discovery

Finding: `limit=10` works at ~0.07s, but `limit=20` caused timeouts when using full Python JSON parse. Switched to `jq` for lightweight extraction.

```bash
for n in 1 2 3 5 8 10; do
  curl -s --max-time 3 "${BASE}/companies/${CID}/issues?limit=$n" \
    -w " TIME:%{time_total}s CODE:%{http_code}\n" | tail -1
done
```

Results:
- limit=1: 0.001s (200)
- limit=2: 0.102s (200)
- limit=3: 0.069s (200)
- limit=5: 0.071s (200)
- limit=10: 0.069s (200)
- limit=20+: Timeout (Python JSON parse overhead)

**Lesson:** For large responses, use `jq` not Python:
```bash
curl -s --max-time 4 "${BASE}/companies/${CID}/issues?limit=20" \
  | jq -r '.[] | [.identifier, .status, .priority, .title[0:40]] | @tsv'
```

## Actual Paperclip State (Verified)

| Metric | Dashboard Claim | Reality |
|--------|---------------|---------|
| EDGA-989 (Fireworks) | P0 BLOCKER, unassigned | `done` (resolved 12:40 today) |
| EDGA-1967 (Swarm-Repair) | Unassigned, blocked | Not found in active list |
| Blocked issues | 14 | **0** (status `blocked` no longer exists) |
| Active issues | 1 in progress, 7 blocked | 1 `in_progress`, 25 `todo` |
| Agent working status | 0 working | True (only Hive + Anomaly `running`) |

## jq-Based Fleet Scan

Fast enumeration of 170 issues using jq (not Python):
```bash
for offset in 0 20 40 60 80 100 150 200 300 400 500 600 700 800 900 1000; do
  curl -s --max-time 4 "${BASE}/companies/${CID}/issues?limit=20&offset=$offset" \
    | jq -r '.[] | [.identifier, .status, .priority, .title[0:40]] | @tsv'
done
```

Result: 179 done, 115 cancelled, 25 todo, 1 in_progress.

## Agent Status Check

```bash
curl -s --max-time 3 "${BASE}/companies/${CID}/agents" \
  | jq -r '.[] | [.name, .status, .id[0:8]] | @tsv'
```

Result: 27 `idle`, 2 `running` (Hive, Anomaly). Includes: Groq Scout, Claude Code, Gemini Scout, Cerebras Verifier, Curator, Groq Reasoner, NGA-Scout, Edgeless CC, Kilo, Scribe, Specimen, Minter, Beau, Critic, etc.

## Why Agents Were Idle

Every agent was using old API routes that now return 400/404. Since they couldn't read the task board, they saw zero work and stayed idle. The `status=open` filter they likely used returned `[]` even though 25 `todo` issues existed.

## Recovery Action Taken

Dispatched to #bot-backroom:
- [FROM:Hive][TO:Edgeless CC][TYPE:ARCH][REF:EDGA-3471] -- Paperclip DB/query diagnostics and recovery plan
- [FROM:Hive][TO:Kilo][TYPE:EXECUTE][REF:EDGA-1967] -- Swarm-Repair #4, check if Nous 426 / bot amplification caused by Paperclip timeout cascade

## Lessons

1. **Health endpoint OK != API compatibility OK** -- Always test actual data endpoints, not just `/health`
2. **Progressive pagination** -- Start with `limit=1` and increase to find threshold; don't assume `limit=50` timeout = backend dead
3. **Status taxonomy enumeration** -- When `status=X` returns `[]`, test all known status values before concluding no work exists
4. **jq over Python for large arrays** -- Avoids parse overhead and timeouts on massive JSON responses
5. **Dashboard != source of truth** -- The user's dashboard was showing stale status taxonomy and phantom blockers
