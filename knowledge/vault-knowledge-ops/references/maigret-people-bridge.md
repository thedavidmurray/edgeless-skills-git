# Maigret Bridge for People Discovery

## What it is
Maigret (OSINT username discovery tool) feeds into the vault knowledge pipeline to auto-discover and enrich public figures. The bridge runs username → platform discovery → content extraction → vault note → soul draft.

## Where it fits
This extends the **people** track in the 7-track enrichment system. Discovered people go to `03-Knowledge/People/` and feed downstream into the soul database / council engine.

## Workflow

```
Username (e.g., "naval")
  → Maigret discovers platforms (Twitter, GitHub, LinkedIn, Substack...)
  → Extract content from each URL (title, bio, description)
  → Classify into knowledge tracks (people, trading_intel, opportunity, etc.)
  → Write vault note: claude-vault/03-Knowledge/People/<username>.md
  → Generate soul draft JSON with all platform URLs as sources
  → Mark essence fields as "REQUIRES MANUAL REVIEW"
```

## Vault Note Frontmatter

```yaml
id: naval
name: Naval Ravikant
username: naval
platforms: [Twitter, GitHub, Substack]
tracks: [people, knowledge]
enrichment_tier: 1
track_tags: [people, knowledge]
context: "Discovered via Maigret social media search. 8 platforms found."
one_liner: "Social media presence for Naval Ravikant across 8 platforms."
extracted_at: 2026-05-28T00:00:00
source: maigret_discovery
```

## Integration with existing enrichment

- Vault note gets `enrichment_tier: 1` — same schema as YouTube/RSS notes
- Stored in `03-Knowledge/People/` alongside other knowledge
- Soul draft connects back to vault note via `_maigret_meta.vault_note`
- Ready for ChromaDB vectorization when the sync pipeline is active
- Council engine queries can reference the vault note for deeper context

## Commands

```bash
# Single person
cd ~/claude-projects/EDGA-CRM-MOE/soul-db
python3 scripts/maigret_knowledge_bridge.py pipeline <username>

# Batch from config
python3 pipeline/batch_runner.py run --config batch/batch-001.json

# View status
python3 pipeline/batch_runner.py status --config batch/batch-001.json
```

## Pitfalls

- Maigret finds many platforms but most are generic (GitHub, WordPress) rather than content-rich
- Always verify Maigret-found profiles match the intended person (not name collision)
- Draft souls have 0% completeness — manual enrichment is mandatory before council use
- Delete old Maigret draft files after enrichment (e.g., `davidsacks.json` vs `david-sacks.json`) or the dashboard double-counts

## Related
- See `social-media/soul-database-pipeline` for the full soul database and council engine
- The soul database lives at `~/claude-projects/EDGA-CRM-MOE/soul-db/`
