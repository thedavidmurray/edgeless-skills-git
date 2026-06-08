---
name: claude-projects-memory-bridge
description: Use when a task depends on the local memory system under .claude/memory or the memory-system skill and you want Codex to reuse those docs and scripts without modifying the originals.
---

# Claude Projects Memory Bridge

## Overview

This skill bridges Codex to the repository's local memory system. Use it to inspect memory docs, config, and scripts under `.claude/memory` while preserving the existing Claude Code setup.

## Use This Skill For

- Understanding how the local memory system is structured
- Reading or updating memory docs and configs under `.claude/memory`
- Manually running or inspecting memory helper scripts when the task requires it
- Explaining what parts of the local memory workflow Codex can and cannot reuse

## Workflow

1. Read `/Users/djm/claude-projects/.claude/skills/memory-system/skill.md` for the local workflow.
2. Read `/Users/djm/claude-projects/.claude/memory/README.md` and relevant config or connector files as needed.
3. If execution is required, verify dependencies and run the local scripts directly.
4. Be explicit when a result comes from docs/config inspection versus script execution.
5. Preserve the original memory files unless the user explicitly wants them changed.

## Important Caveats

- Codex does not auto-run the local memory initialization or restore flow from Claude Code hooks.
- Hook references in `/Users/djm/claude-projects/.claude/settings.json` are configuration context, not native Codex runtime behavior.
- Some memory flows may depend on external tools or stores; verify before claiming they are usable.

## Reading Order

1. Read [references/memory-map.md](references/memory-map.md).
2. Read the local source skill in `/Users/djm/claude-projects/.claude/skills/memory-system/skill.md`.
3. Open only the specific memory docs, configs, or scripts needed for the task.

## Output Expectations

- State whether you used docs, config inspection, or script execution.
- Call out any runtime gaps between Claude Code memory behavior and Codex behavior.
