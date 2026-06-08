---
name: claude-projects-agents-bridge
description: Use when a task should follow one of the local Claude agent profiles under .claude/agents and you want Codex to reuse that agent guidance without modifying the original files.
---

# Claude Projects Agents Bridge

## Overview

This skill bridges Codex to the repository's local Claude agent profiles. Use it when a task matches one of the agent roles in `/Users/djm/claude-projects/.claude/agents/` and the goal is to reuse that guidance manually.

## Use This Skill For

- Following a local agent persona such as `architect`, `review`, `cleanup`, or `workflow-router`
- Understanding how the local agent set is intended to route or specialize work
- Reusing agent-specific expectations while staying inside Codex's tool model

## Workflow

1. Identify the relevant local agent file in `/Users/djm/claude-projects/.claude/agents/`.
2. Read the agent instructions and extract the parts that describe role, scope, and output expectations.
3. Follow those instructions manually within the current Codex session.
4. If the agent is a router, use it as guidance for choosing the right local docs or scripts instead of claiming agent orchestration exists.
5. Preserve the original agent files unless the user explicitly asks to change them.

## Important Caveats

- Codex does not natively spawn the local Claude agents as separate runtimes.
- Agent model settings and colors are metadata for Claude Code, not active Codex configuration.
- Some agent docs refer to skills or tools that may not exist in the current Codex session; verify before relying on them.

## Reading Order

1. Read [references/agents-map.md](references/agents-map.md).
2. Read the specific local agent file needed for the task.
3. Load supporting local skills or command docs only if the selected agent implies them.

## Output Expectations

- State which local agent profile you are following.
- Distinguish clearly between agent guidance and actual Codex runtime capability.
