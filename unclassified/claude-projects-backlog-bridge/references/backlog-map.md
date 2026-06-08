# Backlog Map

## Local Source

- Local skill: `/Users/djm/claude-projects/.claude/skills/backlog-sync/skill.md`
- Runtime config context: `/Users/djm/claude-projects/.claude/settings.json`

## Working Files

- Canonical backlog index: `/Users/djm/claude-projects/backlog/ACTIVE-BACKLOG.md`
- Active task files: `/Users/djm/claude-projects/backlog/tasks/`
- Archived tasks: `/Users/djm/claude-projects/backlog/archive/tasks/`
- Reference docs: `/Users/djm/claude-projects/claude-vault/backlog/README.md`
- Reference guide: `/Users/djm/claude-projects/claude-vault/backlog/BACKLOG-GUIDE.md`

## What Transfers Cleanly

- Task-file review and editing
- ID collision detection
- Backlog/doc consistency checks
- Manual regeneration or normalization work

## What Does Not Transfer Automatically

- Claude Code hook-triggered skill activation
- Any implicit slash-command behavior tied to Claude Code

## Safe Default

Use the local backlog skill as instructions, not as an assumed runtime feature.
