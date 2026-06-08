---
name: claude-projects-local-bridge
description: Use when working inside /Users/djm/claude-projects and the task should reuse the repository's local Claude Code setup under .claude, including local skills, agents, commands, hooks, or script-backed workflows, without modifying the originals or assuming Claude Code runtime features exist in Codex.
---

# Claude Projects Local Bridge

## Overview

This skill bridges Codex to the repository's existing `.claude` ecosystem. It explains how to inspect and reuse local Claude Code skills, agents, commands, hooks, and script-backed workflows while preserving the original files.

## Use This Skill For

- Reusing an existing local `.claude/skills/<skill>/skill.md` workflow
- Following a local agent or command definition in `.claude/agents/` or `.claude/commands/`
- Checking how hooks, permissions, or skill activation work in this repo
- Running local helper scripts bundled under `.claude/skills/*/scripts/`
- Explaining what parts of the local Claude Code setup Codex can and cannot use directly

## Workflow

### 1. Identify the local surface to reuse

- Skills: `.claude/skills/<name>/skill.md` or `.claude/skills/<name>/SKILL.md`
- Agents: `.claude/agents/*.md`
- Commands: `.claude/commands/*.md`
- Hooks and runtime policy: `.claude/settings.json`, `.claude/settings.local.json`, `.claude/hooks/*.py`
- Subagents: `.claude/subagents/*.md`

If the request is broad, read [references/local-claude-map.md](references/local-claude-map.md) first, then open only the relevant local files.

### 2. Decide whether the local asset is reference-only or runnable

- `skill.md` / `SKILL.md` files are instruction sources
- agent and command markdown files are guidance, not native Codex runtime objects
- hooks describe Claude Code runtime behavior; do not assume they auto-run in Codex
- scripts under `.claude/skills/*/scripts/` may be runnable directly if dependencies exist

### 3. Reuse the local workflow with minimal translation

- Prefer the original local skill instructions over re-inventing the workflow
- If the local skill has scripts, inspect and run those rather than rewriting them
- If the local skill references extra docs, load only the specific file needed
- Preserve original file paths and conventions unless the user explicitly asks to migrate them

### 4. Be explicit about runtime differences

- Codex can read and manually follow local `.claude` assets
- Codex does not automatically participate in Claude Code hook execution or slash-command dispatch
- A local agent file is a prompt profile, not a spawned subprocess or separate model instance
- A local command file is usable as a procedural checklist, not a native command binding

### 5. Preserve the originals

- Do not rewrite `.claude/skills`, `.claude/agents`, `.claude/commands`, or `.claude/hooks` unless the user explicitly asks
- Prefer bridge docs, mirror skills, or small compatibility layers over destructive rewrites
- When portability issues matter, call them out separately from usage guidance

## Important Caveats

- This repo's local skill matcher scans `*/skill.md`, not strict `SKILL.md`
- On this machine's case-insensitive filesystem, both casings may appear accessible
- That does not guarantee portability to a case-sensitive environment
- Some local skills rely on secrets, external MCP servers, or local apps; verify dependencies before claiming a workflow is runnable

## Reading Order

1. Read [references/local-claude-map.md](references/local-claude-map.md) for the local layout and caveats.
2. Read the specific local skill, agent, command, or hook relevant to the request.
3. Load local scripts or extra references only if the task requires execution or detailed behavior.

## Output Expectations

- Tell the user whether you are using the local Claude asset as:
  - direct script/tooling
  - procedural reference
  - runtime config reference
- If something is not natively usable in Codex, say so plainly and describe the fallback.
