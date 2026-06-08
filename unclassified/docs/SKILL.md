---
name: docs
description: "Edgeless starter skill: docs"
version: 1.0.0
author: Edgeless
license: MIT
metadata:
  hermes:
    tags: [documentation, docs, edgeless, swarm]
    related_skills: [kb-curation, drafting, review]
---

# Documentation Skill

## Overview

Use this skill for writing, editing, and maintaining project documentation. Focus on clarity, structure, and discoverability.

## When to Use

- README needs updates
- API docs or runbooks needed
- Internal wiki or knowledge base articles
- Onboarding or process documentation

## Workflow

1. **Audience**: Define who reads this and why
2. **Structure**: Outline before writing
3. **Draft**: Write concise, scannable content
4. **Link**: Cross-reference related docs
5. **Review**: Check for accuracy and completeness

## Formatting Rules

- Use Markdown with YAML frontmatter for KB articles
- Code blocks must have language tags
- Use tables for structured data
- Include a "When to Use" section
- Add a verification checklist

## Verification

- [ ] Frontmatter present and valid
- [ ] Links work (or are marked TODO)
- [ ] Code examples are runnable
- [ ] No broken internal references
