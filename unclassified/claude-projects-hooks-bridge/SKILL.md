---
name: claude-projects-hooks-bridge
description: Use when a task depends on the local Claude hook system under .claude/hooks or .claude/settings.json and you want Codex to reuse that behavior as reference without modifying the original hook files.
---

# Claude Projects Hooks Bridge

## Overview

This skill bridges Codex to the repository's local Claude hook system. Use it to inspect hook behavior, troubleshoot hook-side logic, or manually follow hook-driven workflows while preserving the original `.claude/hooks` files.

## Use This Skill For

- Understanding what the local Claude hooks do at prompt, tool, stop, or compact time
- Reviewing or editing hook scripts under `/Users/djm/claude-projects/.claude/hooks/`
- Explaining which hook behavior Codex can mimic manually and which behavior is Claude-only runtime
- Tracing how `.claude/settings.json` wires hook events to scripts

## Workflow

1. Read `/Users/djm/claude-projects/.claude/settings.json` to identify the relevant hook event.
2. Read the specific hook script in `/Users/djm/claude-projects/.claude/hooks/` and any directly referenced helper in `hooks/lib/`.
3. Distinguish between:
   - pure inspection or code reuse
   - manual execution from Codex
   - automatic runtime behavior that only Claude Code provides
4. If a task depends on hook side effects, say plainly whether Codex can reproduce them manually.
5. Preserve the original hook files unless the user explicitly asks to change them.

## Important Caveats

- Codex does not auto-run `.claude/settings.json` hooks.
- `UserPromptSubmit`, `PostToolUse`, `Stop`, and other Claude events are configuration context, not native Codex events.
- Some hook scripts assume Claude-specific input schemas and environment variables; verify those before attempting manual execution.

## Reading Order

1. Read [references/hooks-map.md](references/hooks-map.md).
2. Read `/Users/djm/claude-projects/.claude/settings.json`.
3. Read only the specific hook script and helper modules needed for the task.

## Output Expectations

- State whether the hook behavior is inspectable, manually runnable, or Claude-runtime-only.
- Call out event wiring and dependency assumptions when they matter.
