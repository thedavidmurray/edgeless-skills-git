# Commands Map

## Local Source

- Command docs: `/Users/djm/claude-projects/.claude/commands/`

## High-Value Commands

- Review: `/Users/djm/claude-projects/.claude/commands/review.md`
- Memory: `/Users/djm/claude-projects/.claude/commands/memory.md`
- Cleanup: `/Users/djm/claude-projects/.claude/commands/cleanup.md`
- Status: `/Users/djm/claude-projects/.claude/commands/status.md`
- Test: `/Users/djm/claude-projects/.claude/commands/test.md`

## What Transfers Cleanly

- Procedural guidance from command docs
- Repo-specific conventions encoded in those command files

## What Does Not Transfer Automatically

- Native slash-command invocation
- Claude-only MCP integrations that are unavailable in Codex

## Safe Default

Treat each command file as an instruction sheet and run the underlying steps directly with Codex tools.
