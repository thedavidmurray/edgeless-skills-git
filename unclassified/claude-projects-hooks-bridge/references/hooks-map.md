# Hooks Map

## Local Source

- Hook config: `/Users/djm/claude-projects/.claude/settings.json`
- Hook scripts: `/Users/djm/claude-projects/.claude/hooks/`
- Hook helpers: `/Users/djm/claude-projects/.claude/hooks/lib/`

## Important Entry Points

- Skill suggestion hook: `/Users/djm/claude-projects/.claude/hooks/skill-activation.py`
- Session context hook: `/Users/djm/claude-projects/.claude/hooks/session-start.py`
- Tool usage logging: `/Users/djm/claude-projects/.claude/hooks/post-tool-tracker.py`
- Guardrail hook: `/Users/djm/claude-projects/.claude/hooks/damage-control.py`

## What Transfers Cleanly

- Reading and debugging hook code
- Manual execution of individual scripts when inputs are understood
- Mapping hook events to local workflow expectations

## What Does Not Transfer Automatically

- Claude Code event dispatch
- Automatic hook execution around Codex tool calls
- Implicit environment variables set by Claude runtime

## Safe Default

Treat local hooks as inspectable automation logic and runtime documentation, not as active Codex hooks.
