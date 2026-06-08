# ChromaDB v2 API Raw HTTP Patterns

ChromaDB v2 API (port 8100) is accessed via raw HTTP when the Python client is unavailable or when running from scripts. The v1 API returns 410 Gone.

## Control Character Bug

The v2 `/collections` endpoint returns JSON with raw ASCII control characters in `configuration_json`. These break `json.loads()`:

```python
# Strip all ASCII 0-31 except tab (9), newline (10), carriage return (13)
cleaned = raw.translate({k: None for k in range(32) if k not in [9, 10, 13]})
collections = json.loads(cleaned)
```

Alternative: pipe through `jq` in shell, which handles control characters natively:
```bash
curl -s "http://localhost:8100/api/v2/tenants/default_tenant/databases/default_database/collections" | jq -r '.[] | "\(.id)\t\(.name)\t\(.dimension)"'
```

## Count Endpoint Returns Raw Integer

The v2 count endpoint returns a plain integer string, NOT JSON:

```bash
count=$(curl -s "http://localhost:8100/api/v2/tenants/default_tenant/databases/default_database/collections/$CID/count")
# count is just "12799" — no JSON wrapper
```

In Python, parse with `int(r.text)` directly:
```python
count = int(requests.get(f"{base}/collections/{cid}/count").text)
```

Do NOT use `.json()` — it will fail because the response is not valid JSON.

## Get Documents (Sampling)

```bash
curl -s -X POST "http://localhost:8100/api/v2/tenants/default_tenant/databases/default_database/collections/$CID/get" \
  -H "Content-Type: application/json" \
  -d '{"limit": 10, "offset": 0, "include": ["metadatas", "documents"]}'
```

Returns: `{"ids": [...], "metadatas": [...], "documents": [...]}`

## Where-Document Query (Keyword Search)

```bash
curl -s -X POST "http://localhost:8100/api/v2/tenants/default_tenant/databases/default_database/collections/$CID/get" \
  -H "Content-Type: application/json" \
  -d '{"limit": 5, "where_document": {"$contains": "keyword"}, "include": ["metadatas", "documents"]}'
```

Use for finding docs that mention a topic without needing embeddings.

## Collection Discovery via jq

One-liner to list all collections with counts:
```bash
for cid in $(curl -s $BASE/collections | jq -r '.[].id'); do
  name=$(curl -s "$BASE/collections/$cid" | jq -r '.name')
  count=$(curl -s "$BASE/collections/$cid/count")
  echo "$name: $count"
done | sort -t: -k2 -rn
```

Where `BASE="http://localhost:8100/api/v2/tenants/default_tenant/databases/default_database"`.
