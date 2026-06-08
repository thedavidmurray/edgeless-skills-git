#!/bin/bash
# Verify museum API health — quick smoke test
# Usage: bash verify-museum-apis.sh

echo "=== Museum API Health Check ==="
echo ""

# Wikidata SPARQL
echo -n "Wikidata SPARQL... "
response=$(curl -s -o /dev/null -w "%{http_code}" "https://query.wikidata.org/sparql?query=SELECT%20%2a%20WHERE%20%7B%20%3Fs%20%3Fp%20%3Fo%20%7D%20LIMIT%201" -H "Accept: application/sparql-results+json")
if [ "$response" = "200" ]; then
    echo "✅ OK"
else
    echo "❌ FAIL (HTTP $response)"
fi

# NGA API
echo -n "NGA API... "
response=$(curl -s -o /dev/null -w "%{http_code}" "https://api.nga.gov/v2/artists?name=Test")
if [ "$response" = "200" ]; then
    echo "✅ OK"
else
    echo "❌ FAIL (HTTP $response)"
fi

# MET API
echo -n "MET Open Access... "
response=$(curl -s -o /dev/null -w "%{http_code}" "https://collectionapi.metmuseum.org/public/collection/v1/search?q=test")
if [ "$response" = "200" ]; then
    echo "✅ OK"
else
    echo "❌ FAIL (HTTP $response)"
fi

# Harvard Art Museums (will 403 without key, but server responds)
echo -n "Harvard Art Museums... "
response=$(curl -s -o /dev/null -w "%{http_code}" "https://api.harvardartmuseums.org/person?q=test&apikey=invalid")
if [ "$response" = "401" ] || [ "$response" = "403" ]; then
    echo "✅ OK (requires API key)"
elif [ "$response" = "200" ]; then
    echo "✅ OK"
else
    echo "⚠️ UNEXPECTED (HTTP $response)"
fi

# V&A API
echo -n "V&A API... "
response=$(curl -s -o /dev/null -w "%{http_code}" "https://api.vam.ac.uk/v2/objects/search?q=test&page_size=1")
if [ "$response" = "200" ]; then
    echo "✅ OK"
else
    echo "❌ FAIL (HTTP $response)"
fi

# Art UK
echo -n "Art UK API... "
response=$(curl -s -o /dev/null -w "%{http_code}" "https://api.artuk.org/api/v1/search/results.json?_limit=1")
if [ "$response" = "200" ]; then
    echo "✅ OK"
else
    echo "❌ FAIL (HTTP $response)"
fi

echo ""
echo "=== Check Complete ==="
echo "Note: Some APIs require authentication keys and will return 401/403"
