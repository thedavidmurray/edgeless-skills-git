---
name: claude-projects-n8n-bridge
description: Use when working with n8n workflows in /Users/djm/claude-projects and you want Codex to reuse the local Claude n8n skill and workflow assets without modifying the originals.
---

# Claude Projects N8n Bridge

## Overview

This skill bridges Codex to the repository's local n8n workflow guidance. Use it when inspecting, editing, or troubleshooting workflow assets under `/Users/djm/claude-projects/n8n-workflows` while preserving the original `.claude` skill.

## Use This Skill For

- Reviewing or editing n8n workflow JSON files
- Following the local n8n workflow skill for design or troubleshooting guidance
- Checking repo-specific n8n setup docs, templates, and runtime helpers

## Workflow

1. Read `/Users/djm/claude-projects/.claude/skills/n8n-workflows/skill.md` first.
2. Load the most relevant local docs or references only as needed.
3. Use `/Users/djm/claude-projects/n8n-workflows/` as the working asset directory unless the task says otherwise.
4. Verify environment details such as Docker, credentials, or local services before claiming a workflow is runnable.
5. Preserve the original `.claude` skill and treat it as guidance unless a task explicitly asks to update it.

## Important Caveats

- Codex does not auto-activate the local Claude n8n skill.
- The local n8n reference set is large; keep context small and load only the subset needed for the task.
- Workflow assets may depend on external services, credentials, or a running n8n instance.

## Reading Order

1. Read [references/n8n-map.md](references/n8n-map.md).
2. Read the local source skill in `/Users/djm/claude-projects/.claude/skills/n8n-workflows/skill.md`.
3. Open only the specific workflow JSON, setup doc, or reference file needed for the task.

## Output Expectations

- State whether you used local workflow files, local docs, or runtime verification.
- Be explicit about missing credentials, services, or install prerequisites.
