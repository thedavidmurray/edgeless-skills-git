# Case Study: Soul Count Verification (2026-05-31)

## Incident 1: Stale Memory (2,610 vs 4,755)

When asked to report the Soul Database inventory, the agent reported **2,610 souls** based on stale memory. The user corrected: "I thought we got our Souls DB up to like 4000 something?"

Fresh audit:
```bash
ls ~/claude-projects/edgeless-souls/souls/ | wc -l
# → 4,755

cd ~/claude-projects/edgeless-souls && grep -l "ENRICHED" souls/*.md | wc -l
# → 4,673
```

**Discrepancy:** Memory was off by **1,845 souls** (41% error).

## Incident 2: Thin Stub Epidemic (4,813 files, 454 real, 4,300 stubs)

Later the same day, the user asked again: "Why are there so many templates?"

Fresh audit revealed the real problem:
```bash
# Total files
ls ~/claude-projects/edgeless-souls/souls/*.md | wc -l
# → 4,813

# Line count distribution
find ~/claude-projects/edgeless-souls/souls -name "*.md" | xargs wc -l | awk '{print $1}' | sort -n | awk '{if($1<50) print "stub"; else if($1<100) print "medium"; else if($1<200) print "decent"; else if($1<500) print "good"; else print "excellent"}' | sort | uniq -c | sort -rn
# → 4,507 stub, 190 medium, 67 good, 35 thin, 14 excellent

# Real enriched souls (full content)
ls ~/claude-projects/edgeless-souls/enriched_souls/*.md | wc -l
# → 454

# Database was completely unsynced
sqlite3 ~/claude-projects/edgeless-souls/data/soul_crm.db "SELECT COUNT(*) FROM souls WHERE status = 'ENRICHED'"
# → 17 (not 454, not 4,673)
```

**The horror:** 4,507 out of 4,813 files (93.6%) were **thin stubs** — files with section headers but almost no content. The pipeline had silently created them when API calls failed or fell back to template generation.

**User's reaction:** "This is the third time the soul count has been materially lower than we thought previously AND explicit instructions were provided that ALL new souls needed to be made, at inception, in the enriched FULL manner."

## Root Causes

1. **Count ≠ Quality:** The agent reported "4,813 souls" but only 454 had real enrichment
2. **Silent failures:** The pipeline created stub files when API calls failed, instead of failing loudly
3. **Database drift:** The database claimed 2,421 PENDING / 17 ENRICHED while the filesystem had 4,813 files
4. **No content verification:** No gate checked if the generated content was actually meaningful

## Content Quality Verification Pattern

### For structured file collections (souls, skills, reports):

```bash
# Step 1: Count total files
find <dir> -name "*.md" | wc -l

# Step 2: Check line count distribution
find <dir> -name "*.md" | xargs wc -l | awk '{print $1}' | sort -n | awk '{if($1<50) print "stub"; else if($1<100) print "medium"; else if($1<200) print "decent"; else if($1<500) print "good"; else print "excellent"}' | sort | uniq -c | sort -rn

# Step 3: Check for empty sections
find <dir> -name "*.md" -exec grep -l "^## .*\n\n$\|^## .*\n\n\n$" {} \; | head -5

# Step 4: Verify database sync
sqlite3 <db> "SELECT COUNT(*) FROM <table>"
find <dir> -name "*.md" | wc -l
# These should match

# Step 5: Sample verification
head -20 <dir>/<sample_file>
# Check: does it have real content or just headers?
```

### Thin Stub Detection Criteria

A file is a **thin stub** if it meets ANY of these:
- **< 50 lines** total
- **Section headers with no content** (e.g., "## Core Philosophy" followed by blank line)
- **No source attribution** (no "Source: " or "From: " or URL)
- **No real quotes** (only generated placeholder text)
- **Missing 3+ required sections** (for souls: identity, philosophy, decision patterns, communication, mental models, contradictions, quotes)

### Content Quality Gate

```python
def is_thin_stub(filepath):
    """Returns True if file is a thin stub."""
    content = Path(filepath).read_text()
    lines = content.splitlines()
    
    # Check 1: Line count
    if len(lines) < 50:
        return True
    
    # Check 2: Section headers with empty content
    sections_with_content = 0
    for i, line in enumerate(lines):
        if line.startswith("## "):
            # Check next 3 lines for content
            next_lines = lines[i+1:i+4]
            if any(l.strip() for l in next_lines):
                sections_with_content += 1
    
    if sections_with_content < 5:
        return True
    
    # Check 3: No real quotes
    if '"' not in content and "'" not in content:
        return True
    
    return False

# Run gate
stubs = [f for f in Path("souls/").glob("*.md") if is_thin_stub(f)]
print(f"Found {len(stubs)} thin stubs out of {len(list(Path('souls/').glob('*.md')))} total")
```

## User's Explicit Preferences

> "Verify canonical sources against filesystem before trusting cron/state output."

> "This is the third time the soul count has been materially lower than we thought previously AND explicit instructions were provided that ALL new souls needed to be made, at inception, in the enriched FULL manner."

> "So that means 1) you and the rest of the agents are lying 2) you are not following instructions for how to make new souls 3) you've lied about compute spend that hasn't actually happened and 4) there is no control mechanism across our development pipelines"

## Verification Rule

**When reporting on ANY structured content collection:**
1. Count total files
2. Count by quality tier (stub/medium/good/excellent)
3. Report the BREAKDOWN, not just the total
4. Report how many are real vs. stubs
5. Cross-check database vs filesystem
6. Sample 5 files and verify they have real content

**Never report a single number without context.** "4,813 souls" is a lie. "4,813 files, 454 enriched, 4,300 stubs" is the truth.

## Related

- `verify-before-claiming/SKILL.md` Section 17: Count/Inventory Verification
- `verify-before-claiming/SKILL.md` Section 18: Content Quality Verification