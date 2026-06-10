# Edgeless Skills Repository

Git-backed skills system for the Edgeless swarm. Follows the [GitHub Agent Skills](https://agentskills.io) specification.

## Directory Structure

```
edgeless-skills/
├── creative/          # Creative tasks (writing, design, media)
├── devops/            # Infrastructure, CI/CD, deployment
├── research/          # Investigation, analysis, deep dives
├── product/           # Product management, UX, strategy
├── tooling/           # CLI tools, automation, scripts
├── observability/     # Monitoring, alerting, logging
├── ingestion/         # Data ingestion, ETL, pipelines
├── knowledge/         # Knowledge management, memory, retrieval
├── security/          # Security, threat modeling, compliance
├── system/            # Core platform, gateway, meta-skills
├── external/          # Third-party integrations, APIs
├── unclassified/      # Skills awaiting domain classification
└── scripts/skills/    # Management scripts
```

## Standard Skill Format

Each skill lives in a directory named after the skill and contains at minimum a `SKILL.md` with YAML frontmatter:

```yaml
---
name: skill-name
version: 1.0.0
description: "What this skill does and when to use it."
author: Edgeless
license: MIT
domain: devops
platforms: [linux, macos, windows]
metadata:
  tags: [tag1, tag2]
  related_skills: [other-skill]
  requires_toolsets: [terminal, search_files]
---
```

## Management Scripts

- `scripts/skills/skill_frontmatter.py` — Migrate existing skills to standard frontmatter
- `scripts/skills/skill_sync.py` — Sync local skills to this repo and generate manifest
- `scripts/skills/skill_install.py` — Install skills from GitHub, local paths, or git URLs
- `scripts/skills/session_auto_commit.py` — Auto-commit skill changes after sessions

## Quick Start

```bash
# Sync all local skills into this repo
python scripts/skills/skill_sync.py --commit

# Install a skill from a GitHub repo
python scripts/skills/skill_install.py --source https://github.com/user/repo --skill my-skill

# Auto-commit any pending skill changes
python scripts/skills/session_auto_commit.py
```
