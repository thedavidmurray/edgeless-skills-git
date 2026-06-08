---
title: Cultural Heritage & Museum Collection APIs
name: cultural-heritage-apis
description: Access museum collections, artist databases, and cultural heritage data via SPARQL and REST APIs. Covers Wikidata (artists, birthplaces, artworks), NGA, Harvard Art Museums, MET, Europeana, V&A, Art UK, and other major cultural institutions.
tags:
  - museums
  - wikidata
  - sparql
  - art-history
  - cultural-data
  - api-integration
  - geographic-data
examples:
  - Query Wikidata for 1000+ artists with birthplace coordinates and notable works
  - Enrich artist data with NGA collection objects
  - Build geographic visualization of artists on a map
  - Cross-reference museum APIs for artwork images
---

# Cultural Heritage & Museum Collection APIs

Access **museum collections**, **artist databases**, and **cultural heritage data** programmatically. Primary sources: Wikidata (comprehensive structured data), museum APIs (high-quality images), aggregators (Europeana for scale).

## API Landscape Overview

| Source | Coverage | Key Strength | Auth | Rate Limits |
|--------|----------|--------------|------|-------------|
| **Wikidata SPARQL** | Millions of entities | Birthplaces, dates, relationships, structured links | None | Fair use (~60s timeout, ~500 results practical) |
| **NGA (National Gallery of Art)** | 135K+ objects | High-res open images | None | Generous |
| **Harvard Art Museums** | 224K+ works | Academic depth | API key required | 10,000/day |
| **MET (Metropolitan Museum)** | 500K+ open access | Zero auth required | None | Generous |
| **Europeana** | Millions aggregated | Cross-institution search | API key | 10,000/day |
| **V&A (Victoria & Albert)** | 1M+ objects | Design/craft focus | None | Reasonable |
| **Art UK** | 300K+ UK artworks | Regional UK coverage | None | Standard |
| **Cooper Hewitt** | 200K+ design objects | Smithsonian design | API key | Standard |

## Wikidata SPARQL — Primary Source for Metadata

Wikidata provides **comprehensive structured data** for artists: birthplaces, dates, art movements, notable works, and geographic coordinates.

### Endpoint
```
https://query.wikidata.org/sparql
```

### Essential Query Pattern: Artists with Coordinates
```sparql
SELECT ?artist ?artistLabel ?birthplace ?birthplaceLabel ?coords ?birthYear ?deathYear ?work ?workLabel
WHERE {
  ?artist wdt:P106 wd:Q1028181.           # Occupation: painter
  ?artist wdt:P19 ?birthplace.            # Born at location
  ?birthplace wdt:P625 ?coords.           # Location has coordinates
  
  # Birth/death years
  OPTIONAL { ?artist wdt:P569 ?birthDate. }
  OPTIONAL { ?artist wdt:P570 ?deathDate. }
  
  # Notable paintings
  OPTIONAL { 
    ?artist wdt:P800 ?work.                # Notable works
    ?work wdt:P31 wd:Q3305213.             # Instance: painting
  }
  
  SERVICE wikibase:label { 
    bd:serviceParam wikibase:language "en" 
  }
}
LIMIT 500
```

### Critical Pitfall: Timeout & Pagination

Wikidata SPARQL times out after **60 seconds**. For 1000+ artists:

```python
# Pagination pattern using OFFSET
offsets = [0, 500, 1000, 1500]
all_artists = {}

for offset in offsets:
    query = f"""
    SELECT ... WHERE {{ ... }}
    ORDER BY ?artist
    LIMIT 500
    OFFSET {offset}
    """
    # Request with delay between calls
    time.sleep(2)  # Rate limiting
```

**Rate limit strategy:**
- Add `User-Agent` header with contact info
- 2-3 second delay between paginated queries
- Start with `LIMIT 100` to verify query speed
- Use `ORDER BY` for deterministic pagination

### Data Quality Filters

Not all "painters" in Wikidata are visual artists. Filter for **actual paintings**:

```sparql
# Exclude film directors, musicians, etc.
FILTER EXISTS { ?artist wdt:P800 ?work. ?work wdt:P31 wd:Q3305213. }

# Or require movement association
FILTER EXISTS { ?artist wdt:P135 ?movement. }
```

Common false positives without filtering:
- Film directors (labeled "painter" but only worked in cinema)
- Musicians (painting as hobby, not profession)
- Modern artists with no notable paintings

## Museum API Integration

### NGA (National Gallery of Art)

**URL format:**
```
https://api.nga.gov/v2/objects?artist_id={artist_id}
```

**No authentication required** — completely open.

**Artist lookup:**
```bash
curl -s "https://api.nga.gov/v2/artists?name=Van%20Gogh" | jq '.results'
```

**Image URLs:**
```
https://api.nga.gov/v2/images/{image_id}/large
```

### Harvard Art Museums

**Requires API key:** https://github.com/harvardartmuseums/api-docs

```bash
export HARVARD_API_KEY=your_key_here
curl -s "https://api.harvardartmuseums.org/person?q=artist&apikey=$HARVARD_API_KEY&size=10"
```

**Features:**
- 224K+ objects
- Deep academic metadata
- IIIF image support

### MET Open Access

**No API key required:** https://metmuseum.github.io/

```bash
# Search for objects
curl -s "https://collectionapi.metmuseum.org/public/collection/v1/search?q=impressionism&artistOrCulture=true" | jq '.total'

# Get object details
curl -s "https://collectionapi.metmuseum.org/public/collection/v1/objects/437001" | jq '.primaryImageSmall'
```

**Key fields:**
- `primaryImage`: High-res image URL
- `artistDisplayName`: Artist name
- `objectDate`: Creation date
- `artistBeginDate`/`artistEndDate`: Artist lifespan

### Europeana

**Requires registration:** https://pro.europeana.eu/page/apis

**Aggregates data from 3,000+ institutions**

```bash
curl -s "https://api.europeana.eu/record/v2/search.json?wskey=YOUR_KEY&query=who:Van%20Gogh&rows=10"
```

## Data Fusion Pattern: Scaling Past 500 Results

Real-world applications need **multiple sources**. For 1000+ artists, use **query diversification + deduplication**:

```
Wikidata Query 1: Simple (100 results)
Wikidata Query 2: By movement (50 results)
Wikidata Query 3: By country (50/country × 10 countries = 500 results)
    ↓
Deduplicate by normalized artist name
    ↓
Merged dataset: 1000+ unique artists
```

### Python Implementation

```python
import requests
import json
import time

def fetch_wikidata_simple():
    """Fast, simple query for base dataset"""
    query = '''SELECT ?artist ?artistLabel ?birthplaceLabel ?coords WHERE {
      ?artist wdt:P106 wd:Q1028181. ?artist wdt:P19 ?birthplace.
      ?birthplace wdt:P625 ?coords.
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
    } LIMIT 100'''
    return query_wikidata(query)

def fetch_wikidata_by_movement(movement_qid):
    """Higher-quality artists with verified movements"""
    query = f'''SELECT ?artist ?artistLabel ?birthplaceLabel ?coords WHERE {{
      ?artist wdt:P106 wd:Q1028181. ?artist wdt:P19 ?birthplace.
      ?birthplace wdt:P625 ?coords. ?artist wdt:P135 {movement_qid}.
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" }}
    }} LIMIT 50'''
    return query_wikidata(query)

def fetch_wikidata_by_country(country_qid):
    """Geographic clustering — great for map visualization"""
    query = f'''SELECT ?artist ?artistLabel ?birthplaceLabel ?coords WHERE {{
      ?artist wdt:P106 wd:Q1028181. ?artist wdt:P19 ?birthplace.
      ?birthplace wdt:P625 ?coords. ?birthplace wdt:P17 {country_qid}.
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" }}
    }} LIMIT 50'''
    return query_wikidata(query)

# Merge with deduplication
all_artists = {}

# Base layer
for artist in fetch_wikidata_simple():
    all_artists[artist['name'].lower()] = artist

# Enrichment layers
movements = ['wd:Q40415', 'wd:Q37853', 'wd:Q80113']  # Impressionism, Baroque, Expressionism
for mv in movements:
    for artist in fetch_wikidata_by_movement(mv):
        name = artist['name'].lower()
        if name not in all_artists:
            all_artists[name] = artist
        else:
            # Merge: union of movements
            existing = set(all_artists[name].get('movements', []))
            new = set(artist.get('movements', []))
            all_artists[name]['movements'] = list(existing | new)
    time.sleep(0.3)  # Rate limiting

# Geographic layer
countries = ['wd:Q142', 'wd:Q38', 'wd:Q55']  # France, Italy, Netherlands
for cc in countries:
    for artist in fetch_wikidata_by_country(cc):
        name = artist['name'].lower()
        if name not in all_artists:
            all_artists[name] = artist
    time.sleep(0.3)

# Result: ~1000 unique artists from complementary query slices
```

**Why this works:** Different query dimensions (movement × country × simple) return overlapping but **complementary** result sets. Simple queries get volume; movement queries get quality; country queries ensure geographic coverage.

### Wikidata → Museum API Integration

```python
# 1. Get artists from Wikidata (267 painters with coordinates)
with open('wikidata_painters.json') as f:
    artists = json.load(f)

# 2. Enrich with NGA for artwork images
for artist in artists:
    # Search NGA by name
    nga_url = f"https://api.nga.gov/v2/artists?name={quote(artist['name'])}"
    response = requests.get(nga_url)
    if response.json()['total'] > 0:
        artist['nga_id'] = response.json()['results'][0]['id']
        
        # Fetch their artworks
        artworks_url = f"https://api.nga.gov/v2/objects?artist_id={artist['nga_id']}"
        artworks = requests.get(artworks_url).json()
        artist['artworks'] = artworks['results']
```

### Handling Missing Data

| Gap | Solution |
|-----|----------|
| No images in Wikidata | Link to Wikimedia Commons via titles |
| No birthplace coordinates | Geocode from Wikidata QID |
| Duplicate artist entries | Deduplicate by name + birth year |
| Different movement labels | Normalize to Wikidata QIDs |

## Wikimedia Commons Image Lookup

When Wikidata lacks images, construct Commons search URLs:

```python
def get_commons_url(artist_name, artwork_title):
    # Search Wikimedia Commons
    query = f"{artist_name} {artwork_title}".replace(' ', '_')
    return f"https://commons.wikimedia.org/wiki/Special:Search?search={quote(query)}&go=Go&ns0=1&ns6=1"

# Or use Commons API for programmatic access
api_url = f"https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch={quote(query)}&format=json"
```

## MapLibre GL Integration

For geographic visualization of artists:

```typescript
// Color markers by art movement
const movementColors: Record<string, string> = {
  'Impressionism': '#FF6B6B',
  'Baroque': '#4ECDC4',
  'Renaissance': '#45B7D1',
  'Symbolism': '#96CEB4',
  'default': '#999'
};

// Filter by movement
const filtered = artists.filter(a => 
  selectedMovement === 'All' || 
  a.movements.includes(selectedMovement)
);
```

## Coordinate Parsing

Wikidata returns: `Point(longitude latitude)`

```python
def parse_coords(wkt_point):
    """Parse Wikidata WKT Point format"""
    # Input: "Point(4.89707 52.377956)"
    coords = wkt_point.replace('Point(', '').replace(')', '').split()
    lon = float(coords[0])  # First value is longitude (X)
    lat = float(coords[1])  # Second value is latitude (Y)
    return lat, lon  # Return (lat, lon) for map libraries

# Process SPARQL results
for row in results:
    coords_wkt = row['coords']['value']
    lat, lon = parse_coords(coords_wkt)
    artist['lat'] = lat
    artist['lon'] = lon
```

**Critical:** Wikidata stores `(longitude, latitude)` not `(latitude, longitude)`.

## Quality Filtering

Not all "painters" are visual artists. **Movement-based filtering** yields highest quality:

```python
# Low quality (includes film directors, hobbyists)
simple_artists = query_painters_simple()  # 100 artists

# High quality (verified art historical significance)
movement_artists = query_by_movement('wd:Q40415')  # Impressionism
# Returns: Monet, Renoir, Pissarro (not random "painters")
```

### Movement QIDs for Quality Filtering

| Movement | QID | Typical Results |
|----------|-----|-----------------|
| Impressionism | wd:Q40415 | Monet, Renoir, Pissarro |
| Baroque | wd:Q37853 | Rembrandt, Caravaggio, Rubens |
| Expressionism | wd:Q80113 | Munch, Kirchner, Kandinsky |
| Renaissance | wd:Q1474884 | Raphael, Michelangelo, da Vinci |

> **Pitfall:** The skill previously listed `wd:Q1474884` for both Impressionism and Renaissance. That is wrong. The correct Impressionism QID is `wd:Q40415`. `wd:Q1474884` is a painter *category* for Renaissance artists.

### Data Quality Stats (from 1009 artist dataset)
- **Simple query:** 100% with coordinates, 15% with movements
- **Movement query:** 100% with coordinates, 100% with movements
- **Notable works query:** Significantly slower, 40% timeout rate

**Recommendation:** Use **movement-based queries for quality**, **country-based for quantity**, **simple for baseline coverage**.

## Common Pitfalls

### Wikidata SPARQL Timeout
- **Symptom:** Query returns empty after 60s
- **Fix:** Add `LIMIT 100` first to test, then paginate with `OFFSET`
- **Check:** Start with count query: `SELECT (COUNT(*) AS ?count)`

### Inconsistent Occupation Labels
- **Problem:** "painter" vs "visual artist" vs "artist"
- **Fix:** Query all three QIDs (Q1028181, Q3391743, Q483501)
- **Normalize:** Map to canonical "painter" in output

### Museum API Authentication
- **MET/NGA:** No key needed
- **Harvard/Europeana:** API key required
- **Art UK/V&A:** No key but rate limits apply

### NGA API Endpoint Status (Outage / Deprecation)
- **Symptom:** `curl -s https://api.nga.gov/v2/artists?name=Van%20Gogh` returns HTTP 404
- **Context:** As of 2026-06-03 the documented `https://api.nga.gov/v2/artists` and `https://api.nga.gov/v2/objects` endpoints are unreachable (404 from Cloudflare). The `openaccess-api.nga.gov` subdomain also returns 403.
- **Fix:** Do not rely on NGA as a fallback for MET failures. If the NGA API comes back, verify the endpoint first with a known artist (e.g., `Van Gogh`) before using it in a pipeline.
- **Alternative:** Use MET Open Access exclusively, or supplement with Wikimedia Commons image search.

### MET Search False Positives
- **Symptom:** `search?q=Childe%20Hassam&hasImages=true` returns 33 objectIDs, but many are by unrelated artists (e.g., Paul Gauguin, Gerard David, Hans Memling).
- **Cause:** The MET search endpoint matches artist names loosely across all fields and returns objects that merely *mention* the artist in metadata, or objects where the name was part of a broader query.
- **Fix:** Always verify the `artistDisplayName` field on the individual object endpoint (`/objects/{id}`) before accepting a `primaryImage`. Do not assume the first returned objectID is by the target artist.
- **Pattern:**
  ```bash
  # Search
  ids=$(curl -s ".../search?q=ArtistName&hasImages=true" | jq -r '.objectIDs[]')
  # Verify
  for id in $ids; do
    curl -s ".../objects/$id" | jq '{artistDisplayName: .artistDisplayName, primaryImage: .primaryImage}'
  done
  ```

### Image URL Instability
- Store `objectID` not direct image URLs
- Re-fetch image URLs on demand
- MET images: `primaryImage` field (high-res), `primaryImageSmall` (thumbnail)

## Verification Checklist

Before claiming data integration complete:
- [ ] Cross-reference artist count across sources
- [ ] Verify coordinate format (lat, lon decimal)
- [ ] Confirm image URLs resolve (HTTP 200)
- [ ] Check MET `artistDisplayName` matches target artist before accepting `primaryImage`
- [ ] Check for duplicate artists (same name, different IDs)
- [ ] Validate movement normalization

## References

- `references/wikidata-sparql-examples.md` — Working queries for common patterns
- `references/museum-api-matrix-tested.md` — Auth requirements and endpoint URLs (tested session 2026-04-30)
- `references/museum-api-health-2026-06-03.md` — **Current API status** (NGA down, MET false-positives, verification patterns)
- `scripts/verify-api-health.sh` — Quick health check of all APIs
