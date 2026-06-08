---
name: claude-projects-backlog-bridge
description: Use when working in /Users/djm/claude-projects backlog files and you want Codex to follow the local Claude backlog workflow under .claude/skills/backlog-sync without modifying the original local skill.
---

# Claude Projects Backlog Bridge

## Overview

This skill bridges Codex to the repository's local backlog workflow. Use it to inspect or update `/Users/djm/claude-projects/backlog` while preserving the original `.claude` skill files.

## Use This Skill For

- Reviewing or editing `backlog/ACTIVE-BACKLOG.md`
- Adding, renumbering, or normalizing `backlog/tasks/task-*.md`
- Reconciling backlog docs in `claude-vault/backlog/`
- Reusing the local backlog-sync skill as procedural guidance

## Workflow

1. Treat `/Users/djm/claude-projects/.claude/skills/backlog-sync/skill.md` as the canonical local procedure.
2. Use `/Users/djm/claude-projects/backlog/` as the working backlog unless the task explicitly says otherwise.
3. Preserve existing task IDs and references unless the user asks for renumbering or collision cleanup.
4. When changing backlog structure or docs, update matching `claude-vault/backlog` references if they describe canonical behavior.
5. Surface mismatches between active tasks, archived tasks, and backlog docs as findings.

## Important Caveats

- Codex does not auto-run Claude Code skill activation or backlog-sync hooks.
- Follow the local workflow manually and say when you are using it as reference rather than executable automation.
- Avoid destructive backlog cleanup unless the user asked for it.

## Reading Order

1. Read [references/backlog-map.md](references/backlog-map.md).
2. Read the local source skill in `/Users/djm/claude-projects/.claude/skills/backlog-sync/skill.md`.
3. Open only the specific backlog files needed for the task.

## Output Expectations

- State whether you changed backlog content, docs, or both.
- Put ID collisions, schema drift, stale docs, and archive inconsistencies first.
