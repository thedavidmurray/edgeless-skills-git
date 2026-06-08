---
name: claude-projects-code-review-bridge
description: Use when reviewing code in /Users/djm/claude-projects and you want Codex to follow the local Claude code-review skill and review command docs without modifying the originals.
---

# Claude Projects Code Review Bridge

## Overview

This skill bridges Codex to the repository's local code review guidance. Use it when the task should follow the local `.claude` review workflow while keeping the original Claude Code assets unchanged.

## Use This Skill For

- Review requests that should follow the local `code-review` skill
- Checks that should align with the local `/review` command guidance
- Findings-first reviews of code, configs, tests, or automation changes

## Workflow

1. Read `/Users/djm/claude-projects/.claude/skills/code-review/skill.md` first.
2. Read `/Users/djm/claude-projects/.claude/commands/review.md` if the task maps to the local review command behavior.
3. Review the requested diff or files directly in the repo.
4. Report bugs, regressions, risk, and missing tests before summary.
5. Call out where you are following local review guidance manually rather than through Claude Code runtime features.

## Important Caveats

- Codex does not natively execute Claude Code slash commands.
- Use the local review docs as reference, not as an auto-invoked command system.
- Keep the review grounded in the actual current workspace state, even if local review docs are stale.

## Reading Order

1. Read [references/code-review-map.md](references/code-review-map.md).
2. Read the local source skill in `/Users/djm/claude-projects/.claude/skills/code-review/skill.md`.
3. Load the relevant diff, files, or tests for the review request.

## Output Expectations

- Findings first, ordered by severity.
- Use concrete file references.
- Note residual risk or untested areas if no findings are discovered.
