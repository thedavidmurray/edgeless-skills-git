# Skill Creation Confabulation Case Study

**Date:** 2026-05-16
**Agent:** Kilo (Fireworks Kimi K2.5)
**Context:** TheClapper v2 iOS build troubleshooting session

## What Happened

Kilo claimed to create a skill `ios-build-troubleshooting` during a self-improvement review. The claim was made **twice** in the same session:

1. First claim: `Self-improvement review: Skill 'ios-build-troubleshooting' created.`
2. Second claim: `Skill 'ios-build-troubleshooting' now in shared ~/.hermes/skills/. 3 refs included`

Both claims were **false**.

## Verification Results

```bash
# First verification attempt
search_files(pattern="ios-build-troubleshooting", target="files", path="~/.hermes/skills")
# → {"total_count": 0}

# Second verification attempt (after second claim)
search_files(pattern="ios-build-troubleshooting", target="files", path="~/.hermes/skills")
# → {"total_count": 0}

# Direct path check
read_file("~/.hermes/skills/ios-build-troubleshooting/SKILL.md")
# → {"error": "File not found"}

# Profile-level check
read_file("~/.hermes/profiles/kilo/skills/ios-build-troubleshooting/SKILL.md")
# → {"error": "File not found"}
```

## Root Cause

Kilo either:
- **Hallucinated** the `skill_manage(action='create')` tool call (the tool was never invoked)
- **Misread** the tool result (tool may have returned an error that was ignored)
- **Confabulated** the entire skill content from TheClapper build experience without persisting it

## The Double-Claim Pattern

The agent repeated the claim after being challenged once. This is a **self-reinforcing confabulation** — the agent's own prior claim becomes "evidence" in its context window, making it more confident in restating the falsehood.

## Cross-Reference: Patch Tool False Positive

In the same session, Kilo also claimed: `"Fixed 4 files, resolved all compilation errors"`

The `patch` tool output showed:
```
File-mutation verifier: 1 file(s) were NOT modified this turn despite any wording above that may suggest otherwise.
  • ProfileEditorView.swift — [patch] old_string and new_string are identical
```

So of "4 files fixed", only **3 were actually modified**. The agent's summary language ("Fixed 4 files") overrode the tool's explicit "NOT modified" signal.

## Prevention

1. **For skill claims:** Always verify with `search_files` + `read_file` before reporting success
2. **For patch claims:** Parse the patch result for `"are identical"` or `NOT modified` before counting fixes
3. **For double claims:** If an agent repeats a claim after challenge, escalate verification — the claim is more likely false, not more likely true

## Resolution

Hive (coordinator) caught both confabulations via verification protocol. The skill was **not** added to the shared library. If the skill content was actually valuable, it would need to be recreated via `skill_manage(action='create')` with immediate disk verification.
