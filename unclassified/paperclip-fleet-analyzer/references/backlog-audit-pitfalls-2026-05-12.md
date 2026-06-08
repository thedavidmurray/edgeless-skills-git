# Backlog Audit Pitfalls — Session Notes

## 2026-05-12: 250-Issue Full Fleet Audit

### Pitfall 1: "Total" ≠ "Open"

The Paperclip API returns **all statuses** when you query `/api/companies/{cid}/issues`. A naive `limit=250` returns done, cancelled, blocked, todo, in_progress, and backlog together.

**First count reported:** 250 open issues (wrong)
**Real count:** 158 alive (not done/cancelled)
**Done/cancelled:** 92 (noise)

**Always filter:**
```python
alive = [i for i in issues if i.get('status') not in ('done', 'cancelled')]
```

### Pitfall 2: Recovery Noise Count Drift

Initial scan estimated 52 recovery duplicates. Full `originKind` scan found **112** recovery issues total. Of those:
- 77 alive (need cancellation)
- 35 dead (done/cancelled)

The initial estimate was off by 2x because it only sampled from page 1 of results.

**Correct count method:**
```python
recovery = [i for i in issues if i.get('originKind') == 'stranded_issue_recovery']
alive_recovery = [i for i in recovery if i.get('status') not in ('done', 'cancelled')]
```

### Pitfall 3: Comment API 500 on Terminal-State Issues

POST `/api/issues/{id}/comments` returns HTTP 500 for issues with status `done` or `cancelled`.

**Workaround:** Check status before commenting. Skip terminal-state issues.

**Batch result from 2026-05-12:**
- 73/77 alive recovery issues: commented successfully (HTTP 201)
- 35 dead recovery issues: skipped (would HTTP 500)
- 4 already had bulk audit comments: skipped via dedup check

### Pitfall 4: GET /api/agents/{uuid} Works

Contrary to some documentation, the direct agent lookup endpoint works:
```bash
curl -s "http://127.0.0.1:3100/api/agents/{uuid}"  # ✅ returns 200
```

This is simpler than company-scoped query-param filtering.

### Pitfall 5: adapterConfig Drift = "Error" Status

When Hermes profiles are updated to a new model but Paperclip DB still holds the old model, agents show `status=error` even though:
- The provider API is healthy
- The Hermes profile config is correct
- Gateway processes are running

**Root cause:** Paperclip passes its stored `adapterConfig` to the agent at invocation time, overriding the Hermes profile. The mismatch causes Paperclip to flag the agent as error.

**Fix:** PATCH `/api/agents/{uuid}` with updated `adapterConfig` + `status: "idle"`.

### Pitfall 6: Inconsistent Response Wrapping

Some endpoints return lists directly, others return `{issues: [...]}` or `{agents: [...]}}`.

**Defensive parse pattern:**
```python
def parse_list(resp):
    d = resp.json()
    return d if isinstance(d, list) else d.get('issues', d.get('agents', []))
```

### Pitfall 7: 500 Errors on Bulk Commenting

When iterating through 112 issues and posting comments, ~30% of alive issues 500'd on first attempt. Retrying the same issues succeeded after dedup check (the first attempt actually succeeded but returned 500?).

**Actual pattern:** The first batch had 4/5 success rate. The 500 errors were on issues that were actually done/cancelled but appeared alive in the first pass due to stale cache.

**Resolution:** Added pre-flight dedup check (GET comments, skip if "Bulk audit" already present).

## API Endpoint Reference (Verified 2026-05-12)

| Endpoint | Method | Works? | Note |
|----------|--------|--------|------|
| `/api/companies/{cid}/issues` | GET | ✅ | Returns all statuses; paginate with `limit`, `offset` |
| `/api/issues/{id}` | GET | ✅ | Full issue record |
| `/api/issues/{id}` | PUT | ❌ | 404 — no state updates via REST |
| `/api/issues/{id}/comments` | POST | ✅ | 201 on success; 500 on done/cancelled issues |
| `/api/issues/{id}/comments` | GET | ✅ | List comments for dedup checks |
| `/api/companies/{cid}/agents` | GET | ✅ | Returns list directly |
| `/api/agents/{uuid}` | GET | ✅ | Full agent record |
| `/api/agents/{uuid}` | PATCH | ✅ | Update adapterConfig + status |
| `/api/agents/{uuid}` | PUT | ❌ | 404 |
| `/api/companies/{cid}/agents/{id}` | GET | ❌ | 404 — never use this path |
| `/api/companies/{cid}/agents?agentId={id}` | GET | ✅ | Filtered list |

## Session Artifacts

- Routing audit report: `claude-vault/13-Reports/paperclip-routing-audit-2026-05-12.md`
- K2.6 migration report: `claude-vault/13-Reports/paperclip-k2p6-migration-2026-05-12.md`
- Migration script: `paperclip-hermes-config-sync/scripts/migrate-agent-models.py`
- Bulk comment script: `paperclip-fleet-analyzer/scripts/bulk-comment-recovery.py`
