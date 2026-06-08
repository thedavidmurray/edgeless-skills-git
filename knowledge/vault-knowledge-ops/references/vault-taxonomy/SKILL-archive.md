---
name: vault-taxonomy-enforcement
description: Enforce canonical vault structure, detect and remediate taxonomy collisions, migrate content from wrong locations, and prevent future drift via damage-control protection. Covers the complete workflow from detection through migration to prevention.
trigger: user mentions wrong vault location, taxonomy collision, numbered folder conflict, canonical path issue, vault migration, or structure cleanup
---

# Vault Taxonomy Enforcement

Enforce the single source of truth for vault structure per TAXONOMY.md v3.

## Quick Reference: Canonical Locations

| Location | Canonical Path | Wrong Path (BLOCKED) |
|----------|---------------|---------------------|
| Vault | `~/claude-projects/claude-vault/` | `~/claude-vault/` ❌ |
| Projects | `~/claude-projects/projects/` | `~/Projects/` ❌ |
| Backlog | `~/claude-projects/backlog/` | `*/backlog/tasks/` ❌ |
| Config | `~/.claude/`, `~/config/` | `*/05-config/` ❌ |

## Taxonomy v3 Numbered Folders

| # | Folder | Purpose | Status |
|---|--------|---------|--------|
| 00 | 00-Inbox | Quick capture | ✅ |
| 01 | 01-Journal | Daily notes | ✅ |
| 02 | 02-Agents | Agent personas | ✅ |
| 03 | 03-Knowledge | Research/KB | ✅ |
| 04 | 04-Sessions | Session logs | ✅ |
| 05 | 05-Solutions | Problem-solution | ✅ |
| 06 | 06-Config | Configuration | ✅ |
| 07 | 07-Business | Business strategy | ✅ |
| 08 | 08-Reference | External refs | ✅ |
| 09 | 09-Secrets | Credentials | ✅ |
| 10 | 10-Meta | Meta-docs | ✅ |
| 11 | 11-Databases | Bases/Chroma | ✅ |
| 12 | *RESERVED* | Future use | 🔒 |
| 13 | 13-Reports | All reports | ✅ |
| 14 | 14-Knowledge-Bases | Structured KB | ✅ |
| 15 | 15-Products | Product docs | ✅ |
| 16 | 16-Projects | Project docs | ✅ |
| 17 | 17-Websites | Website builds | ✅ |
| 99 | 99-Archive | Cold storage | ✅ |

## Collision Detection

Run taxonomy validator:
```bash
python3 .claude/hooks/validate-taxonomy.py --check
```

Common collisions to watch for:
- `06-*`: 06-Config (canonical) vs 06-Projects (deprecated, merge to 16-Projects)
- `14-*`: 14-Knowledge-Bases (canonical) vs 14-Evaluation (deprecated, renumber to 18-Evals)

## Migration Workflow

### Step 1: Analyze Wrong Location
```python
from pathlib import Path

wrong_vault = Path("/Users/djm/claude-vault")
correct_vault = Path("/Users/djm/claude-projects/claude-vault")

# Check if wrong location exists and has content
if wrong_vault.exists():
    items = list(wrong_vault.iterdir())
    print(f"Wrong vault has {len(items)} items")
    for item in items:
        print(f"  {item.name}")
```

### Step 2: Identify Conflicts
For each item in wrong location:
- Check if same name exists in correct location
- Compare file sizes/content hashes
- Flag duplicates vs unique content

### Step 3: Migrate Content
- **Files**: Move to correct location (rename if conflict)
- **Directories**: Merge if exists, move if unique
- **Git repos**: Preserve `.git/` during move

### Step 4: Cleanup
- Remove empty directories from wrong location
- Delete wrong location when empty

### Step 5: Add Protection
Update `~/.claude/hooks/patterns.yaml` to block future writes:
```yaml
# WRONG PATH BLOCKING
- '^/Users/djm/claude-vault/'     # BLOCK: Non-canonical vault
- '^/Users/djm/Projects/'          # BLOCK: Wrong projects
- '^~/claude-vault/'              # BLOCK: Home vault (tilde)
- '^~/Projects/'                   # BLOCK: Home projects (tilde)
```

## Pitfalls

### Path Resolution Bug
❌ **Wrong**: `Path.home() / "claude-vault"`  
✅ **Right**: `PROJECT_ROOT / "claude-vault"`

### Double-Nesting Bug
❌ **Wrong**: `Path("~/claude-vault") / "claude-vault" / "03-Knowledge"`  
✅ **Right**: `PROJECT_ROOT / "claude-vault" / "03-Knowledge"`

### Collision During Migration
When both locations have same folder name:
1. Compare file counts and sizes
2. Merge unique files
3. Rename conflicts with `-wrong-vault` suffix
4. Flag for manual review if sizes differ

### Git History Loss
- Always use `shutil.move()` for directories with `.git/`
- Never use `mv` across filesystems (breaks hard links)
- Verify `.git/` preserved after move

## Generated Media Artifacts — Where Renders Go

When a user provides a media file (video, image, audio) and asks for processed output, **never default to `~/Desktop/` as the output path.** Always route through the canonical taxonomy.

**User preference (strong signal — May 2026):** "no we don't do it to desktop, figure out based on our fucking taxonomy where this should go in claude-projects or the subfolder of that /claude-vault and make sure it's aligned with our taxonomy"

### Workspace Roots for Transient/Bulky Output

Per `TAXONOMY.md` v3, generated artifacts (renders, screenshots, model outputs, temporary build output) go to **workspace roots outside the indexed vault**:

| Artifact Type | Canonical Workspace | Example |
|---------------|---------------------|---------|
| Video renders, loops, exports | `~/claude-projects/generated/` | `generated/warning-icon-loop-30s.mp4` |
| Screenshots, screen captures | `~/claude-projects/captures/` | `captures/touchdesigner-preview.png` |
| General build/model output | `~/claude-projects/output/` | `output/newsletter_digest.html` |
| HTML artifacts, design mockups | `~/claude-projects/generated/` or project subdir | `generated/hermes-design-system/` |

### Decision Flow for Media Output

```
User provides media → process with ffmpeg/tool → where to write?
    ├── Is it a transient render/model output?
    │   ├── YES → `~/claude-projects/generated/` (or `captures/` / `output/`)
    │   └── NO → Continue ←
    ├── Is it durable project knowledge (notes, reports, decisions)?
    │   ├── YES → `~/claude-projects/claude-vault/<numbered-folder>/`
    │   └── NO → Continue ←
    └── Is it live source code / dependency tree?
        ├── YES → `~/claude-projects/projects/` or `~/claude-projects/tools/`
        └── NO → Ask user or default to `generated/`
```

### Anti-Patterns

**❌ WRONG — Desktop default:**
```python
# Agent ships to Desktop without asking
output_path = "~/Desktop/warning-icon-loop-30s.mp4"
```

**❌ WRONG — Vault root pollution:**
```python
# Writing transient renders into the indexed note surface
output_path = "~/claude-projects/claude-vault/warning-icon-loop-30s.mp4"
```

**✅ CORRECT — Taxonomy-routed output:**
```python
# Ask if a subfolder makes sense, default to generated/
subfolder = "generated/warning-icons/" if is_recurring_asset else "generated/"
output_path = f"~/claude-projects/{subfolder}warning-icon-loop-30s.mp4"

# VERIFY: path exists after write
ls_result = terminal(f"ls -la {output_path}")
if ls_result.exit_code == 0:
    print(f"✓ Verified: {output_path}")
```

### Pre-Write Check

Before writing any media artifact, check the existing workspace subdirectories to see if an owning project already has a folder:

```bash
ls ~/claude-projects/generated/ | grep -i "video\|media\|render\|asset"
# If a project-specific folder exists (e.g., generated/hive/ or generated/edgelesslab/),
# prefer that over the generic root.
```

### Integration with Other Skills

| Skill | Output Type | Canonical Path |
|-------|-------------|----------------|
| `comfyui` | AI-generated images/video | `~/claude-projects/generated/comfyui/` |
| `ascii-video` | ASCII art MP4/GIF | `~/claude-projects/generated/ascii-video/` |
| `manim-video` | Math animation MP4 | `~/claude-projects/generated/manim/` |
| `image_gen` | AI-generated images | `~/claude-projects/generated/` |
| `touchdesigner-mcp` | TD renders/screenshots | `~/claude-projects/captures/touchdesigner/` |

---

## Automated Vault Synthesis

Beyond one-time remediation, run a scheduled compilation agent that cross-references ChromaDB + vault markdown to detect drift, generate MOCs, and surface contradictions before they compound.

### What the Agent Does
1. **Queries ChromaDB** — pulls recent embeddings from domain-relevant collections
2. **Scans vault markdown** — finds files matching knowledge domain keywords
3. **Detects contradictions**:
   - Duplicate folders (normalized string collision: `OnChain-Art` vs `On-Chain-Art`)
   - Stale wiki links (`[[Generative Art Fundamentals]]` with no target file)
4. **Generates MOC pages** — Map of Content per domain with cross-references, topic counts, and source inventory
5. **Writes idempotently** — content-hash deduplication prevents duplicate writes

### Running the Agent
```bash
# Dry run (safe default — previews what would change)
DRY_RUN=1 python scripts/vault-compilation-agent.py

# Apply writes (only when preview looks correct)
APPLY=1 python scripts/vault-compilation-agent.py
```

### Cron Schedule
```cron
# Weekly synthesis — Sundays at 3 AM
0 3 * * 0 cd ~/claude-projects && DRY_RUN=1 python scripts/vault-compilation-agent.py >> /tmp/vault-synthesis.log 2>&1

# Monthly full apply — first Sunday
0 3 1-7 * 0 cd ~/claude-projects && APPLY=1 python scripts/vault-compilation-agent.py >> /tmp/vault-synthesis-apply.log 2>&1
```

## Protection Verification

Test that protection works:
```bash
# This should be blocked by damage-control.py
echo "test" > ~/claude-vault/test.txt
```

### Hash Consistency Bug (Idempotency)
When computing content hashes for idempotent writes, the verification must use **exactly** the same input as the generation step. Any difference (join order, whitespace, truncation boundary) causes false-positive rewrites.

❌ **Wrong**: Generate hash from `all_text[:500]` in MOC, but verify against `" ".join(d["content"][:500] for d in docs)` — different join behavior, different hash.  
✅ **Right**: Store the exact hash-computation expression in a variable and reuse it:
```python
all_text_for_hash = " ".join(d.get("content", "") for d in chroma_docs + vault_files)
file_hash = fingerprint(domain + all_text_for_hash[:500])
# Use file_hash in both generation and verification
```

## References

- `references/vault-collision-remediation.md` - Session recipes for specific collision types
- `references/vault-compilation-agent-pattern.md` - Full synthesis agent design pattern
- `templates/vault-compilation-agent.py` - Starter template for new compilation agents
- `~/.claude/hooks/patterns.yaml` - Active protection patterns
- `~/.claude/hooks/validate-taxonomy.py` - Taxonomy validator
- `~/claude-projects/claude-vault/_system/TAXONOMY.md` - Canonical structure definition