---
name: edgeless-guard
title: Edgeless Guard Compliance Runtime
version: 0.1.0
description: Runtime compliance guard for Hermes deployments. Enforces HIPAA/SOX/FINRA/EU AI Act policies on agent tool use, output, and workflows.
category: security
triggers:
  - compliance
  - guard
  - audit
  - hipaa
  - sox
  - finra
  - eu-ai-act
inputs:
  command:
    description: Subcommand to run.
    required: true
    enum: [init, check, enforce, report, validate, version]
  target:
    description: Path to file/directory/command to audit.
    required: false
    format: string
  policy:
    description: Policy profile to apply.
    required: false
    enum: [hipaa, sox, finra, eu-ai-act, custom]
outputs:
  report:
    path: .edgeless-guard/reports/
    format: json,txt
---

# Edgeless Guard Compliance Runtime

**Install**: `hermes skill install ~/.hermes/skills/edgeless-guard` (or symlink via `scripts/install-skill.sh`).  
**Usage**: `edgeless-guard <command>` after skill load.  
**Guard modes**: `warn` (report only) | `block` (halt on violation) | `log` (record, no halt).

## The Job (from edgelesslab.com)

Ship a production-ready compliance guard that makes Hermes agents audit-ready for regulated industries.  
Mitigate regulatory risk in agentic AI workflows without sacrificing utility.

## Scope

- Runtime guard layer for tool use and agent output
- Compliance policy schema (JSON Schema)
- Report exporter (JSON + human-readable)
- Unit tests (installed)

## Commands

| Command | Description |
|---------|-------------|
| `init` | Install guard into a profile (`~/.hermes/`). |
| `check <target>` | Scan a path or command string for violations. |
| `enforce <target>` | Execute target under guard; block on violations if mode=block. |
| `report <run-id>` | Print/summarize a report by ID. |
| `validate` | Validate current policy files against schema. |
| `version` | Print version. |

## Installation

After copying to `~/.hermes/skills/edgeless-guard/`:

```bash
# Install hook wiring
~/.hermes/skills/edgeless-guard/bin/edgeless-guard init

# Validate policy files
~/.hermes/skills/edgeless-guard/bin/edgeless-guard validate
```

## Policy Profiles

Prebuilt profiles live in `references/policies/`:

- `hipaa.yaml` — PHI handling, encryption, access control
- `sox.yaml` — SOX IT general controls, change management
- `finra.yaml` — Communication archiving, supervisory review
- `eu-ai-act.yaml` — Risk classification, high-risk AI rules

Create a custom profile by copying a template and editing YAML.

## Guard Modes

- `warn`: Log and print violations, allow execution to continue
- `block`: Halt execution, exit non-zero on violation
- `log`: Record only, no stdout/stderr noise

Set via policy root key `guard.mode`.

## Test Suite

```bash
~/.hermes/skills/edgeless-guard/bin/edgeless-guard self-test
# or
python3 ~/.hermes/skills/edgeless-guard/tests/test_edgeless_guard.py
```

## Guarantees

- Installable as a Hermes skill
- Guard modes work
- Tests pass on launch
- Produces JSON + human-readable reports
