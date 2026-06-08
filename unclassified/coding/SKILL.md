---
name: coding
description: "Edgeless starter skill: coding"
version: 1.0.0
author: Edgeless
license: MIT
metadata:
  hermes:
    tags: [coding, development, edgeless, swarm]
    related_skills: [review, planning, ops-alert]
---

# Coding Skill

## Overview

Use this skill for writing, editing, and running code. Focus on correctness, testability, and clean structure.

## When to Use

- User asks for code implementation
- Refactoring existing code
- Debugging a specific issue
- Writing scripts or automation

## Workflow

1. **Understand**: Read existing code, understand context
2. **Plan**: Sketch approach before typing
3. **Implement**: Write minimal, correct code
4. **Test**: Run tests or verify manually
5. **Commit**: Report what was done with evidence

## Principles

- Prefer explicit over implicit
- Handle errors, don't swallow them
- Add docstrings and type hints
- Run `pytest` or `python -m` to verify
- Respect `.gitignore` and existing conventions

## Verification

- [ ] Code runs without errors
- [ ] Edge cases considered
- [ ] Existing tests still pass
- [ ] Output shown in response
