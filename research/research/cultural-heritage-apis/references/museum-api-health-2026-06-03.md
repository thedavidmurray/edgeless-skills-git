# Museum API Health Check — Session 2026-06-03

## Context

This report was generated during the weekly fxhash style-seed brief pipeline. It documents the *current* availability of the museum APIs referenced in the cultural-heritage-apis skill.

## Results

| API | Auth | Status | Notes |
|-----|------|--------|-------|
| **Wikidata SPARQL** | None | ✅ Working | 3 movement queries (Impressionism Q40415, Baroque Q37853, Expressionism Q80113) returned 15+ artists each |
| **NGA API** | None | ❌ **Down** | `api.nga.gov/v2/artists` returns HTTP 404 (Cloudflare). `openaccess-api.nga.gov` returns 403 |
| **MET Open Access** | None | ✅ Working | Search + object endpoints functional. *Critical caveat: search returns false positives* |
| **Harvard Art Museums** | API Key | ⚠️ Untested | No key available in this session |
| **Europeana** | API Key | ⚠️ Untested | No key available in this session |

## NGA API — Detailed Failure

**Endpoint:** `https://api.nga.gov/v2/artists?name=Van%20Gogh`

**Response:**
```
HTTP/2 404
server: cloudflare
```

**Body:** Apache `Not Found` HTML page.

**Variants tested (all 404 or 403):**
- `https://api.nga.gov/v2/artists?name=Van%20Gogh`
- `https://api.nga.gov/v1/artists?name=Van%20Gogh`
- `https://api.nga.gov/artists?name=Van%20Gogh`
- `https://api.nga.gov/openapi/v1/artists`
- `https://openaccess-api.nga.gov/v1/artists?name=Van%20Gogh` → HTTP 403

**Conclusion:** The NGA API endpoints documented in the skill are currently unreachable. The previous 2026-04-30 test confirmed they were working, so this is a regression or migration. Do not rely on NGA as a fallback.

## MET Open Access — Detailed Behavior

**Search endpoint:**
```bash
curl -s "https://collectionapi.metmuseum.org/public/collection/v1/search?q=Childe%20Hassam&hasImages=true"
```

**Returns:** 33 objectIDs.

**Problem:** Only a minority of the returned objectIDs are actually by Childe Hassam. The first 10 IDs included works by:
- Gerard David
- Paul Gauguin
- Hans Memling
- Thomas Rowlandson
- Bartolomé Estebán Murillo
- William Blake

**Root cause:** The MET search endpoint matches the query string loosely across all object metadata (title, artist, culture, tags, description). It does not guarantee the artist name in the query is the `artistDisplayName`.

**Verification pattern:**
```bash
# 1. Search
ids=$(curl -s ".../search?q=ArtistName&hasImages=true" | jq -r '.objectIDs[]')

# 2. Verify each object until a match is found
for id in $ids; do
  obj=$(curl -s ".../objects/$id")
  artist=$(echo "$obj" | jq -r '.artistDisplayName')
  if [ "$artist" = "ArtistName" ]; then
    echo "$id is valid: $(echo "$obj" | jq -r '.primaryImage')"
    break
  fi
done
```

## Verified Cross-References (This Session)

| Artist | Movement | MET Object ID | Title | primaryImage URL |
|--------|----------|---------------|-------|------------------|
| Guido Reni | Baroque | 437422 | Charity | https://images.metmuseum.org/CRDImages/ep/original/DT10776.jpg |
| Frans Hals | Baroque | 436616 | Young Man and Woman in an Inn | https://images.metmuseum.org/CRDImages/ep/original/DP145899.jpg |
| Giovanni Battista Tiepolo | Baroque | 437798 | The Glorification of the Barbaro Family | https://images.metmuseum.org/CRDImages/ep/original/DP287646.jpg |
| Gian Lorenzo Bernini | Baroque | 206399 | Bacchanal: A Faun Teased by Children | https://images.metmuseum.org/CRDImages/es/original/DP248148.jpg |
| Camille Pissarro | Impressionism | 437310 | The Boulevard Montmartre on a Winter Morning | https://images.metmuseum.org/CRDImages/ep/original/DP-21959-001.jpg |
| Camille Pissarro | Impressionism | 437299 | Jalais Hill, Pontoise | https://images.metmuseum.org/CRDImages/ep/original/DT1859.jpg |

## Recommendations

1. **For artist metadata:** Wikidata SPARQL remains the primary source.
2. **For artwork images:** Use MET Open Access, but *always* verify `artistDisplayName` on the object endpoint.
3. **For NGA fallback:** Do not use. The API is currently unreachable.
4. **For next session:** Re-test NGA with a simple `curl` to `https://api.nga.gov/v2/artists?name=Van%20Gogh` before assuming it is back.
