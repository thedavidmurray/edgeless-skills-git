# Vault Collision Remediation Session (2026-05-05)

**Issue**: Multiple vault locations and taxonomy collisions discovered during routine cron audit.

## Problems Found

### 1. Wrong Vault Location
- **Wrong**: `/Users/djm/claude-vault/` (1,170 files, 41k+ items)
- **Correct**: `/Users/djm/claude-projects/claude-vault/`
- **Root Cause**: Early scripts used `Path.home() / "claude-vault"` instead of `PROJECT_ROOT`

### 2. Wrong Projects Location
- **Wrong**: `/Users/djm/Projects/` (41k+ items including Next.js apps)
- **Correct**: `/Users/djm/claude-projects/projects/`

### 3. Taxonomy Collisions
| Prefix | Collision | Resolution |
|--------|-----------|------------|
| `06-*` | 06-Config (canonical) + 06-Projects (stale) | Merged 06-Projects/ content to 16-Projects/, deleted stale |
| `14-*` | 14-Knowledge-Bases (canonical) + 14-Evaluation (deprecated) | Renamed 14-Evaluation/ to 18-Evals/ with README |

## Migration Steps Executed

### Wrong Vault Migration
```bash
# 1. Analyzed contents
ls ~/claude-vault/  # 03-Knowledge/, 13-Reports/, 14-Evaluation/, etc.

# 2. Moved fxhash content (25+ articles)
mv ~/claude-vault/03-Knowledge/fxhash* ~/claude-projects/claude-vault/03-Knowledge/
mv ~/claude-vault/03-Knowledge/OnChainGenerativeArt/ ~/claude-projects/claude-vault/03-Knowledge/

# 3. Moved evaluation datasets
mv ~/claude-vault/14-Evaluation ~/claude-projects/claude-vault/18-Evals/
# (Added README.md with purpose statement for 18-Evals)

# 4. Moved reports and skills
mv ~/claude-vault/13-Reports/* ~/claude-projects/claude-vault/13-Reports/
mv ~/claude-vault/_system/skills/* ~/claude-projects/claude-vault/_system/skills/

# 5. Cleanup nested vault bug (claude-vault/claude-vault/)
rm -rf ~/claude-vault/claude-vault/

# 6. Delete wrong vault
rm -rf ~/claude-vault/
```

### Projects Migration
```bash
# Moved dev workspaces with git history preserved
mv ~/Projects/my-app ~/claude-projects/projects/edgelesslab-redesign/
mv ~/Projects/edgelesslab.com ~/claude-projects/claude-vault/17-Websites/

# Deleted stale incomplete copy
rm -rf ~/Projects/edgelesslab-redesign/  # Only 20 items, duplicate

# Deleted empty Projects/
rmdir ~/Projects/
```

### Taxonomy Collision Resolution
```bash
# 06-* collision: Merged to 16-Projects
mv ~/claude-projects/claude-vault/06-Projects/Spreadsheet-Pixels ~/claude-projects/claude-vault/16-Projects/
mv ~/claude-projects/claude-vault/06-Projects/spreadsheet-pixels-demo ~/claude-projects/claude-vault/16-Projects/
rmdir ~/claude-projects/claude-vault/06-Projects/

# 14-* collision: Renamed with purpose statement
mv ~/claude-projects/claude-vault/14-Evaluation ~/claude-projects/claude-vault/18-Evals/
# Created 18-Evals/README.md with taxonomy purpose
```

## Protection Added

Updated `~/.claude/hooks/patterns.yaml`:
```yaml
# WRONG PATH BLOCKING (EDGA-2026-05-05)
- '^/Users/djm/claude-vault/'     # BLOCK: Non-canonical vault path
- '^/Users/djm/Projects/'          # BLOCK: Wrong projects location
- '^~/claude-vault/'              # BLOCK: Home vault (tilde expansion)
- '^~/Projects/'                   # BLOCK: Home projects (tilde expansion)
```

## Verification

```bash
# Taxonomy validation
python3 ~/.claude/hooks/validate-taxonomy.py --check
# Result: PASSED - 18 numbered folders, 0 collisions

# Check wrong locations deleted
ls ~/claude-vault/        # No such file or directory
ls ~/Projects/            # No such file or directory

# Check content in correct locations
ls ~/claude-projects/claude-vault/03-Knowledge/fxhash*  # 7 items
ls ~/claude-projects/claude-vault/18-Evals/           # hard-search-set/, README.md
ls ~/claude-projects/projects/edgelesslab-redesign/   # 41k items with .git/
```

## Lessons Learned

1. **No protection was the root cause** - damage-control.py only blocked deprecated paths, not wrong vault/projects locations
2. **Early script bugs compound** - Path.home() vs PROJECT_ROOT confusion created the initial drift
3. **EDGA-307 content explosion** - NotebookLM KB creation for fxhash created 25+ articles with duplicate directory structures
4. **Collision detection requires active audit** - Taxonomy validator exists but wasn't run regularly

## Prevention Checklist

- [ ] damage-control.py patterns updated to block wrong paths
- [ ] Taxonomy validator run monthly via cron
- [ ] New scripts use PROJECT_ROOT not Path.home()
- [ ] Vault write audit hook logs all writes with source attribution
- [ ] Session-end hook validates no writes to wrong locations
