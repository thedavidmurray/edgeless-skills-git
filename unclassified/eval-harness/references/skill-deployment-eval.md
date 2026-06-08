# Skill Deployment Eval Pattern

## When to Use

You just deployed 3+ new skills from an external repo (ECC, hub, or manual import) and need to verify they actually work in your environment. This pattern runs each skill against a real file, config, or task to surface integration gaps before they become production blockers.

## Pattern: 3-Phase Parallel Eval

### Phase 1: Deploy (sequential)
- Copy skill files to `~/.hermes/skills/<category>/<skill-name>/`
- Verify skill loads with `skill_view(name)`
- Fix any syntax errors before proceeding

### Phase 2: Parallel Test (3-5 subagents)
- Assign 1 skill per subagent
- Give each subagent a real target (file, config, or task)
- Set a timeout (e.g., 120s) to prevent hangs
- Run all subagents in parallel with `delegate_task`

### Phase 3: Assembly & Scoring
- Collect all subagent results
- Score each skill: PASS (worked), PARTIAL (needs config), FAIL (broken)
- Document integration gaps in the eval report
- Prioritize fixes: P0 = broken skill, P1 = missing config, P2 = minor gap

## Example: 5 Skills from ECC Repo

**Skills deployed**: `security-review`, `deep-research`, `mcp-server-patterns`, `everything-claude-code`, `bun-runtime`

**Tests assigned**:
| Skill | Target | Result |
|-------|--------|--------|
| security-review | `chroma_vault_sync_pipeline.py` | ✅ 83% (missing CLI bounds checks) |
| deep-research | "Bun vs Node 2026" | ⚠️ 0% (firecrawl/exa MCP not configured) |
| mcp-server-patterns | `~/.mcp.json` | ✅ 50% (missing timeouts, version pinning) |
| everything-claude-code | `ecc.js` | ✅ 100% (conventions match) |
| bun-runtime | `package.json` | ✅ 100% (good analysis) |

**Average pass rate**: 67%

**Integration gaps found**:
- `deep-research` requires firecrawl or exa MCP → no fallback when unavailable
- `mcp-server-patterns` audit caught missing timeouts in `~/.mcp.json`
- `security-review` found missing CLI bounds checks in pipeline code

## Key Pitfalls

1. **MCP dependency failures** — Skills that depend on MCP servers (firecrawl, exa) fail silently if not configured. Always verify MCP availability before assigning the skill.
2. **Subagent timeout** — Large file reads (e.g., 608-line Python file) can cause subagent timeout. Pre-scan file sizes and break large files into chunks.
3. **Tool call mismatches** — Subagents may try tools that don't exist in their environment (e.g., `exa_search` without the MCP). Catch these with `skill_view` first.
4. **No test targets** — A skill needs a real target to evaluate. If the user's codebase has no JS files, `everything-claude-code` is untestable.

## Scoring Rubric

| Grade | Criteria | Action |
|-------|----------|--------|
| ✅ 100% | Skill works perfectly, no issues | Deploy to production |
| ✅ 80-99% | Minor gap, fixable in <10 min | Patch and re-test |
| ⚠️ 50-79% | Needs config or dependency | Document requirement, fix before production |
| ❌ <50% | Skill fundamentally broken or mismatched | Don't deploy, debug or replace |

## Fast Re-Test After Fixes

After fixing an issue (e.g., adding MCP config), re-test only the failed skill:

```python
# Re-test deep-research after adding firecrawl MCP
python3 << 'PYEOF'
# Verify MCP is available
mcp_check = terminal("mcp list | grep firecrawl")
if mcp_check:
    # Re-run the eval
    result = deep_research_eval("Bun vs Node 2026")
    print(f"Re-test score: {result['score']}")
PYEOF
```

## Template: Eval Report

```markdown
# EVAL REPORT: skill-deployment-batch-N

## Skills Deployed
- [skill-name] (category) — [source]

## Test Results

| Skill | Target | Score | Notes |
|-------|--------|-------|-------|
| ... | ... | ... | ... |

## Integration Gaps
1. [Gap description] — [Fix needed]

## Action Items
- [ ] Fix gap 1
- [ ] Re-test failed skills
- [ ] Deploy to production

## Status: [NEEDS FIX / READY]
```
