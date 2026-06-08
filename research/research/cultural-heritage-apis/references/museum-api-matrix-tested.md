# Museum API Test Results — Session 2026-04-30

## Summary of API Testing

Tested 8+ museum/cultural APIs for artist data integration.

## Results

| API | Auth | Status | Notes |
|-----|------|--------|-------|
| **Wikidata SPARQL** | None | ✅ Working | Primary source for 267 artists + coordinates |
| **NGA API** | None | ✅ Working | 4 artists matched (Van Gogh, Picasso, Monet, da Vinci) with 409 artworks |
| **Harvard Art Museums** | API Key | ⚠️ Needs auth | Timed out on test (no key provided) |
| **MET Open Access** | None | ✅ Working | Returned `{"total":0}` for test query (needs better query params) |
| **Europeana** | API Key | ⚠️ Needs auth | Blocked as private/internal address in browser test |
| **V&A API** | None | ⚠️ Unclear | Empty response on test |
| **Art UK** | None | ⚠️ Unclear | Empty response on test |
| **Cooper Hewitt** | API Key | ⚠️ Needs auth | No response on spec endpoint |

## Detailed Findings

### NGA API — Successfully Used

**Base URL:** `https://api.nga.gov/v2/`

**Artist search:**
```bash
curl -s "https://api.nga.gov/v2/artists?name=Van%20Gogh"
```

**Artworks by artist:**
```bash
curl -s "https://api.nga.gov/v2/objects?artist_id={id}"
```

**Matched artists in session:**
- Vincent van Gogh: 23 objects
- Pablo Picasso: 324 objects  
- Claude Monet: 31 objects
- Leonardo da Vinci: 31 objects

**Total artworks enriched:** 409

### Wikidata SPARQL — Primary Source

**Endpoint:** `https://query.wikidata.org/sparql`

**Yielded:** 267 painters with:
- Birthplace coordinates (lat/lon)
- Birth/death years
- Art movements (25+ movements)
- Notable painting titles

**Data quality after filtering:**
- 267 actual painters (vs 500 unfiltered with false positives)
- All have coordinates via P625
- Represented movements: Symbolism (14), Baroque (13), Impressionism (12), Romanticism (12), etc.

### MET API — Partial

**Search endpoint:**
```bash
curl -s "https://collectionapi.metmuseum.org/public/collection/v1/search?q=impressionism&artistOrCulture=true"
```

Returns object IDs, then fetch details:
```bash
curl -s "https://collectionapi.metmuseum.org/public/collection/v1/objects/{id}"
```

**Key fields:**
- `primaryImage`: High-res URL
- `primaryImageSmall`: Thumbnail
- `artistDisplayName`: Artist name
- `objectDate`: Creation date

### APIs Requiring Keys (Not Tested)

- **Harvard:** `https://api.harvardartmuseums.org/` — needs API key
- **Europeana:** `https://api.europeana.eu/` — needs registration
- **Cooper Hewitt:** Smithsonian design collection — needs key

## Recommendations

1. **For geographic artist data:** Wikidata SPARQL (free, comprehensive)
2. **For artwork images:** NGA (no auth) + MET (no auth)
3. **For academic depth:** Get Harvard API key
4. **For cross-institution search:** Get Europeana key

## Integration Pattern

```
Wikidata SPARQL
    ↓ (267 artists with coordinates, movements, dates)
    
NGA API
    ↓ (enrich 4 major artists with 409 artwork images)
    
MapLibre GL
    ↓ (geographic visualization with movement filters)
```
