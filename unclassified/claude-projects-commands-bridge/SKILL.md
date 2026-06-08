---
name: claude-projects-commands-bridge
description: Use when a task maps to the local Claude slash-command docs under .claude/commands and you want Codex to follow those procedures without modifying the original command files.
---

# Claude Projects Commands Bridge

## Overview

This skill bridges Codex to the repository's local Claude command set. Use it when a task corresponds to a local slash command and the goal is to follow its documented workflow manually in Codex.

## Use This Skill For

- Reusing procedures documented in `/Users/djm/claude-projects/.claude/commands/*.md`
- Mapping a user request to the local `/review`, `/memory`, `/cleanup`, `/status`, or similar command guidance
- Explaining what a local Claude slash command would do in this repo

## Workflow

1. Identify the closest local command file under `/Users/djm/claude-projects/.claude/commands/`.
2. Read that command doc and extract the procedural parts relevant to the task.
3. Execute the workflow manually with Codex tools instead of pretending the slash command exists natively.
4. If the command depends on Claude-only runtime, say so and provide the closest Codex fallback.
5. Preserve the original command docs unless the user explicitly asks to change them.

## Important Caveats

- Codex does not natively execute the local slash commands.
- Some command docs assume MCP tools or Claude-specific runtime surfaces that may not exist in Codex.
- Follow the intent of the command, but keep the result grounded in the actual current workspace and tool availability.

## Reading Order

1. Read [references/commands-map.md](references/commands-map.md).
2. Read the specific local command file needed for the task.
3. Load extra local docs or scripts only if the task requires them.

## Output Expectations

- Name the local command you are following as reference.
- Be explicit when you are using a manual Codex fallback instead of native command execution.
