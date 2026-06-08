# Wikidata SPARQL Patterns: Artist Geographic Data

Session: 2026-04-30 — Artist Map Visualization

## Working Queries

### 1. SIMPLIFIED Query — Most Reliable (100-500 results, fast)
```sparql
SELECT ?artist ?artistLabel ?birthplace ?birthplaceLabel ?coords WHERE {
  ?artist wdt:P106 wd:Q1028181.
  ?artist wdt:P19 ?birthplace.
  ?birthplace wdt:P625 ?coords.
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
}
LIMIT 100
```
**Use this FIRST** — Complex joins with OPTIONAL cause timeouts. Start simple, enrich in follow-up queries.

### 2. By Art Movement — Quality Filter (50-100 results)
```sparql
SELECT ?artist ?artistLabel ?birthplaceLabel ?coords ?movementLabel WHERE {
  ?artist wdt:P106 wd:Q1028181.
  ?artist wdt:P19 ?birthplace.
  ?birthplace wdt:P625 ?coords.
  ?artist wdt:P135 ?movement.
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
}
LIMIT 50
```
**Movement-based queries return higher-quality artists** (verified art historical significance).

### 3. By Country — Geographic Clustering (50 results/country)
```sparql
SELECT ?artist ?artistLabel ?birthplace ?birthplaceLabel ?coords WHERE {
  ?artist wdt:P106 wd:Q1028181.
  ?artist wdt:P19 ?birthplace.
  ?birthplace wdt:P625 ?coords.
  ?birthplace wdt:P17 wd:Q142.  # France (Q142), Italy (Q38), etc.
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
}
LIMIT 50
```
**Country codes:** Q142=France, Q38=Italy, Q55=Netherlands, Q29=Spain, Q183=Germany, Q30=USA, Q145=UK, Q159=Russia, Q31=Belgium, Q40=Austria

### 4. With Notable Works — Data Rich (200 results, slower)
```sparql
SELECT ?artist ?artistLabel ?birthplaceLabel ?coords ?work ?workLabel WHERE {
  ?artist wdt:P106 wd:Q1028181.
  ?artist wdt:P19 ?birthplace.
  ?birthplace wdt:P625 ?coords.
  ?artist wdt:P800 ?work.
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
}
LIMIT 200
```
**Use only when you need artwork titles** — significantly slower.

## Multi-Source Scaling Strategy (1000+ Artists)

**Problem:** Single queries timeout at ~500 results. **Solution:** Multiple simple queries + deduplication.

### Pattern: Staggered Collection + Deduplication
```python
all_artists = {}

# Source 1: Simple base query
simple_batch = query_wikidata(simple_query, limit=100)
for artist in simple_batch:
    all_artists[artist['name'].lower()] = artist

# Source 2: Movement-based (different slice)
movement_batch = query_wikidata(movement_query, limit=50)
for artist in movement_batch:
    name = artist['name'].lower()
    if name not in all_artists:
        all_artists[name] = artist  # New artist
    else:
        # Merge data (movements, additional works)
        existing_movements = set(all_artists[name].get('movements', []))
        new_movements = set(artist.get('movements', []))
        all_artists[name]['movements'] = list(existing_movements | new_movements)

# Source 3-N: Country-based (different countries)
countries = ['wd:Q142', 'wd:Q38', 'wd:Q55', ...]  # France, Italy, Netherlands...
for country_qid in countries:
    country_query = build_country_query(country_qid)
    country_batch = query_wikidata(country_query, limit=50)
    # Same merge logic as above

# Result: 267 + 155 + 98 + 125 + 494 = 1009 unique artists
```

**Key insight:** Querying by different dimensions (movement × country × simple) yields overlapping but complementary sets. Deduplication by normalized name gives clean union.

### Rate Limiting for Multi-Source
```python
time.sleep(0.3)  # 300ms between country queries
# 10 countries × 300ms = 3 seconds total — well under limits
```

## Rate Limiting Notes

- **Timeout:** 60 seconds hard limit
- **Practical limit:** ~500 results per query for complex joins
- **Pagination:** Use `ORDER BY ?artist` + `OFFSET` + `LIMIT`
- **Delay:** 2-3 seconds between paginated requests

## Python Execution Pattern

```python
import requests
import json

endpoint = "https://query.wikidata.org/sparql"
headers = {'Accept': 'application/sparql-results+json', 'User-Agent': 'Mozilla/5.0'}

query = """SELECT ..."""

response = requests.get(
    endpoint,
    params={'query': query},
    headers=headers,
    timeout=60
)

# Parse coordinates from "Point(lon lat)" format
results = response.json()['results']['bindings']
for row in results:
    coords = row['coords']['value']  # "Point(4.89 52.37)"
    lon, lat = map(float, coords.replace('Point(', '').replace(')', '').split())
```

## Data Quality Issues Encountered

1. **False positives:** Film directors returned as "painters" (e.g., Hitchcock)
   - Fix: Add `FILTER EXISTS` for actual painting works

2. **Missing coordinates:** Some birthplace Q-items lack P625
   - Mitigation: Geocode from location name or skip

3. **Multiple movements:** Some artists have 3-4 movements
   - Normalization needed for UI display

## Coordinate Format

Wikidata returns: `Point(longitude latitude)`
- Example: `Point(4.89707 52.377956)` = Amsterdam
- Always parse as `(lon, lat)` not `(lat, lon)`

## Entity Types Used

| QID | Meaning |
|-----|---------|
| Q1028181 | painter (occupation) |
| Q3305213 | painting (artwork type) |
| P106 | occupation |
| P19 | place of birth |
| P625 | coordinate location |
| P569 | date of birth |
| P570 | date of death |
| P800 | notable work |
| P135 | movement |
| P31 | instance of |
