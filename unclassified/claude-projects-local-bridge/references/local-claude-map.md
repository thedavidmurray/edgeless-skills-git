# Local Claude Map

## Scope

This repository has an existing Claude Code setup under `/Users/djm/claude-projects/.claude/`.

Use it as a local capability map, not as proof that Codex automatically inherits Claude Code runtime behavior.

## Main Surfaces

### `.claude/skills/`
- Primary source for local reusable workflows
- Most skills use `skill.md`
- One visible exception uses strict `SKILL.md` (`remotion`)
- Some skills include runnable helpers under `scripts/`

### `.claude/agents/`
- Prompt profiles for specialized roles
- Good for behavior guidance and workflow structure
- Not native spawned agents in Codex

### `.claude/commands/`
- Slash-command style operational playbooks
- Use them as checklists or procedures

### `.claude/hooks/`
- Runtime hooks used by Claude Code
- Referenced by `.claude/settings.json`
- Useful for understanding local policy and automation boundaries
- Do not assume they auto-run in Codex

### `.claude/settings.json`
- Main hook wiring
- Good source of truth for which hooks matter in this repo

### `.claude/settings.local.json`
- Local allowlists and environment-specific permissions
- Useful for understanding what the original setup expected to be available

## High-Value Local Skills

Start here when the request overlaps:

- `article-extractor`
- `backlog-sync`
- `code-review`
- `dev-docs`
- `memory-system`
- `n8n-workflows`
- `research-deep`
- `skill-creator`
- `test-driven-development`
- `verify-completion`

## Practical Rules

1. Prefer reading the original local skill over paraphrasing it from memory.
2. If a local skill has scripts, inspect those before re-implementing logic.
3. Preserve the original `.claude` files unless the user explicitly wants migration or cleanup.
4. Separate "Codex can read this" from "Codex can execute this".
5. Call out case-sensitivity risks when local files rely on lowercase `skill.md`.
