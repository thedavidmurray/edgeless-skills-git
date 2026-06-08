# Memory Map

## Local Source

- Local skill: `/Users/djm/claude-projects/.claude/skills/memory-system/skill.md`
- Memory overview: `/Users/djm/claude-projects/.claude/memory/README.md`
- Memory config: `/Users/djm/claude-projects/.claude/memory/configs/memory_sources.yaml`
- Memory initializer: `/Users/djm/claude-projects/.claude/memory/session_initializer.py`
- Memory coordinator: `/Users/djm/claude-projects/.claude/memory/memory_coordinator.py`

## Supporting Context

- Hook config reference: `/Users/djm/claude-projects/.claude/settings.json`
- Restore helper: `/Users/djm/claude-projects/.claude/memory/restore_memory.sh`
- Connectors: `/Users/djm/claude-projects/.claude/memory/connectors/`

## What Transfers Cleanly

- Reading memory docs and configs
- Inspecting connector layout
- Running local helper scripts manually when dependencies exist

## What Does Not Transfer Automatically

- Session-start memory restoration
- Hook-triggered initialization
- Any implicit Claude Code memory loading

## Safe Default

Use the memory system as inspectable local infrastructure, not as an auto-loaded Codex capability.
