# ChromaDB Sync Script — Silent Failure Pattern (2026-06-04)

## Incident Summary

The daily cron job `chroma-sync-daily` (runs at 03:00) had been reporting **success** for days while producing **zero actual embeddings** in the target collection.

### Pre-Run Script Output (Provided by Cron)
```
[2026-06-04T03:17:44] [INFO] Vault → ChromaDB Sync Started (full=False, dry_run=False)
[2026-06-04T03:17:44] [INFO] Initial unified_knowledge count: -1
[2026-06-04T03:17:52] [INFO] Incremental sync: files modified since 2026-05-28T10:42:22
[2026-06-04T03:17:55] [INFO] Found 1193 markdown files in vault
[2026-06-04T03:17:55] [INFO] Files needing processing: 1193
[2026-06-04T03:17:55] [INFO] Deleting 77 outdated entries...
[2026-06-04T03:18:46] [INFO] Sync Complete in 62.7s
[2026-06-04T03:18:46] [INFO] Files processed: 1193
[2026-06-04T03:18:46] [INFO] Embeddings inserted: 2224
[2026-06-04T03:18:46] [INFO] Errors: 0
[2026-06-04T03:18:46] [INFO] Collection count: -1 → -1
```

### Red Flags in the Output

1. **`-1 → -1`**: The collection count was `-1` at both start and end. `-1` is the error fallback value from `chroma_count()`, not a real count.
2. **No verification step**: The script never queried the collection to confirm inserts were stored.
3. **`Errors: 0`**: The error counter only tracked Python `Exception` during file processing, not HTTP failures from batch insert operations.

## Root Cause

The script `sync-vault-to-chroma.py` hardcoded `COLLECTION_ID = "0da87c14-02ec-4cc9-ae2c-18d273534014"`. The `unified_knowledge` collection had never been created with that ID. Every REST API call to `/collections/{COLLECTION_ID}/add` returned **HTTP 404**, but the script's `chroma_insert_batch()` function returned `False` on failure — and the calling code in `flush_batch()` only logged the error, never incremented an error counter or aborted the sync.

```python
# The failure path (original code)
def flush_batch(batch, state, dry_run):
    success = chroma_insert_batch(...)
    if not success and not dry_run:
        log(f"Failed to insert batch of {len(batch)} documents", "ERROR")
    # No: error counter increment, no abort, no propagate
```

## Why This Is a Confabulation Pattern

| Claim in Output | Reality | Why It Was Wrong |
|---|---|---|
| "Embeddings inserted: 2224" | 0 stored | HTTP 404 on every `/add` call |
| "Errors: 0" | 2224+ failures | Error counter only counted `Exception`, not `False` return |
| "Collection count: -1 → -1" | Collection didn't exist | `-1` is the error code, not a count |
| "Sync Complete" | No data persisted | No post-sync verification was performed |

## The Fix

### 1. Create the Missing Collection
```bash
curl -s -X POST http://localhost:8100/api/v2/tenants/default_tenant/databases/default_database/collections \
  -H "Content-Type: application/json" \
  -d '{"name":"unified_knowledge","metadata":{"created_by":"hive-sync"}}'
# Response: {"id":"e02f9823-42c7-4c49-a5f3-811edfbcb9ef",...}
```

### 2. Patch Script to Lookup Collection ID Dynamically
Instead of hardcoding a UUID that may or may not exist, the script now queries the collections list by name:

```python
def get_collection_id() -> str:
    """Look up collection ID by name (robust across restarts)."""
    url = f"{CHROMA_BASE}/tenants/{TENANT}/databases/{DATABASE}/collections"
    resp = requests.get(url, timeout=10)
    for col in resp.json():
        if col.get("name") == COLLECTION_NAME:
            return col["id"]
    return COLLECTION_ID  # Fallback to hardcoded
```

All `chroma_insert_batch`, `chroma_delete_by_ids`, `chroma_count`, and `verify_sync` functions now call `get_collection_id()` at runtime.

### 3. Verify After Sync

```python
# After run_sync completes:
final_count = chroma_count()  # Now returns a real number
assert final_count > 0, "Sync produced zero documents — investigate"
```

## Verification Checklist for ChromaDB Sync Jobs

Before reporting a sync as complete:

- [ ] `chroma_count()` returns a non-negative integer (not `-1`)
- [ ] Post-sync count > pre-sync count (or == pre-sync count if incremental with no changes)
- [ ] Query a known phrase and get back documents with metadata
- [ ] The collection ID resolves to an existing collection via `/collections` list
- [ ] If the script reports `Errors: 0`, confirm the error counter actually tracks HTTP failures

## Historical Context

The `chroma` skill's `references/vault-sync-pipeline.md` documents a similar collection ID mismatch fix for `chroma_vault_sync_pipeline.py` (dated 2026-06-02). This incident involves a different script (`sync-vault-to-chroma.py`, the cron entrypoint) with the same root cause: **hardcoded collection IDs that don't match the live database**. The more robust fix is dynamic lookup rather than updating a hardcoded ID to a different hardcoded ID.

## Prevention

1. **Always use dynamic collection lookup** by name in sync scripts. Hardcoded UUIDs are fragile across ChromaDB restarts, migrations, or recreation.
2. **Verify the collection exists before the first insert.** A missing collection should abort the sync with a clear error, not silently log "0 errors".
3. **Add a post-sync verification query.** Even a simple `collection.count()` or `collection.query()` confirms data actually persisted.
4. **Make the error counter track ALL failures.** HTTP 4xx/5xx, batch insert `False`, and file-processing exceptions should all increment the same counter.
