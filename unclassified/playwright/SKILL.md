---
name: "playwright"
description: "Use when the task requires automating a real browser from the terminal (navigation, form filling, snapshots, screenshots, data extraction, UI-flow debugging) via `playwright-cli` or the bundled wrapper script."
---


# Playwright CLI Skill

Drive a real browser from the terminal using `playwright-cli`. Prefer the bundled wrapper script; it uses the globally installed CLI when present and falls back to `npx` when it is not.
Treat this skill as CLI-first automation. Do not pivot to `@playwright/test` unless the user explicitly asks for test files.

## Prerequisite check (required)

Before proposing commands, check whether `playwright-cli` or `npx` is available:

```bash
command -v playwright-cli >/dev/null 2>&1 || command -v npx >/dev/null 2>&1
```

If neither is available, pause and ask the user to install Node.js/npm and `@playwright/cli`. Provide these steps verbatim:

```bash
# Verify Node/npm are installed
node --version
npm --version

# If missing, install Node.js/npm, then:
npm install -g @playwright/cli@latest
playwright-cli --help
```

Once either `playwright-cli` or `npx` is present, proceed with the wrapper script. A global install of `playwright-cli` is preferred for faster startup, but not required.

## Skill path (set once)

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export PWCLI="$CODEX_HOME/skills/playwright/scripts/playwright_cli.sh"
```

User-scoped skills install under `$CODEX_HOME/skills` (default: `~/.codex/skills`).

## Quick start

Use the wrapper script:

```bash
"$PWCLI" open https://playwright.dev --headed
"$PWCLI" snapshot
"$PWCLI" click e15
"$PWCLI" type "Playwright"
"$PWCLI" press Enter
"$PWCLI" screenshot
```

If the user prefers the direct binary, this is also valid:

```bash
npm install -g @playwright/cli@latest
playwright-cli --help
```

## Core workflow

1. Open the page.
2. Snapshot to get stable element refs.
3. Interact using refs from the latest snapshot.
4. Re-snapshot after navigation or significant DOM changes.
5. Capture artifacts when useful. Prefer screenshot, snapshot, console, network,
   DOM HTML, and raw CLI outputs. Treat traces as optional only when known-good.

Minimal loop:

```bash
"$PWCLI" open https://example.com
"$PWCLI" snapshot
"$PWCLI" click e3
"$PWCLI" snapshot
```

## When to snapshot again

Snapshot again after:

- navigation
- clicking elements that change the UI substantially
- opening/closing modals or menus
- tab switches

Refs can go stale. When a command fails due to a missing ref, snapshot again.

## Recommended patterns

### Form fill and submit

```bash
"$PWCLI" open https://example.com/form
"$PWCLI" snapshot
"$PWCLI" fill e1 "user@example.com"
"$PWCLI" fill e2 "password123"
"$PWCLI" click e3
"$PWCLI" snapshot
```

### Debug a UI flow without relying on traces

```bash
"$PWCLI" open https://example.com --headed
"$PWCLI" snapshot
"$PWCLI" screenshot
"$PWCLI" console
"$PWCLI" network
"$PWCLI" eval "document.documentElement.outerHTML"
```

### Multi-tab work

```bash
"$PWCLI" tab-new https://example.com
"$PWCLI" tab-list
"$PWCLI" tab-select 0
"$PWCLI" snapshot
```

## Wrapper script

The wrapper script prefers a globally installed `playwright-cli` and falls back to `npx --package @playwright/cli playwright-cli` when needed:

```bash
"$PWCLI" --help
```

Prefer the wrapper unless the repository already standardizes on the direct `playwright-cli` binary.

## References

Open only what you need:

- CLI command reference: `references/cli.md`
- Practical workflows and troubleshooting: `references/workflows.md`

## Guardrails

- Always snapshot before referencing element ids like `e12`.
- Re-snapshot when refs seem stale.
- Prefer explicit commands over `eval` and `run-code` unless needed.
- When you do not have a fresh snapshot, use placeholder refs like `eX` and say why; do not bypass refs with `run-code`.
- Use `--headed` when a visual check will help.
- When capturing artifacts in this repo, use `output/playwright/` and avoid introducing new top-level artifact folders.
- The local CLI trace commands are currently unreliable; prefer snapshot/screenshot/console/network/DOM artifacts first.
- Default to CLI commands and workflows, not Playwright test specs.
