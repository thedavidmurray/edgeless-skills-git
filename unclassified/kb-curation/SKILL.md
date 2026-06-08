---
name: kb-curation
description: "Edgeless starter skill: kb-curation"
version: 1.0.0
author: Edgeless
license: MIT
metadata:
  hermes:
    tags: [kb, knowledge, curation, edgeless, swarm]
    related_skills: [docs, scribe, research]
---

# Knowledge Base Curation Skill

## Overview

Use this skill to maintain, organize, and improve the knowledge base.

## When to Use

- New knowledge needs to be captured
- Existing articles are outdated
- Inbox items need processing
- Knowledge structure needs reorganization

## Workflow

1. **Ingest**: Collect new items from inbox, sessions, or research
2. **Evaluate**: Is this worth keeping? Is it accurate?
3. **Synthesize**: Merge with existing knowledge or create new
4. **Structure**: Place in correct category with tags
5. **Archive**: Move processed items out of inbox

## KB Structure

```
00-Inbox/       → Raw incoming items
01-Processing/  → Items being worked
02-Reference/   → Quick lookup facts
03-Knowledge/   → Curated articles
04-Archive/     → Outdated but retained
```

## Article Format

```markdown
---
title: "Article Title"
date: YYYY-MM-DD
tags: [tag1, tag2]
source: url or session-id
---

# Title

## Context
Why this matters

## Content
What we know

## References
Links to sources
```

## Verification

- [ ] Frontmatter complete
- [ ] Content is accurate and dated
- [ ] Cross-references added
- [ ] Inbox item archived after processing
- [ ] Duplicates merged or noted
