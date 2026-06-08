#!/usr/bin/env bash
set -euo pipefail

has_session_flag="false"
for arg in "$@"; do
  case "$arg" in
    --session|--session=*|-s|-s=*)
      has_session_flag="true"
      break
      ;;
  esac
done

if command -v playwright-cli >/dev/null 2>&1; then
  # Prefer the globally installed CLI to avoid npx startup overhead.
  cmd=(playwright-cli)
elif command -v npx >/dev/null 2>&1; then
  # Fall back to npx so the wrapper still works without a global install.
  cmd=(npx --yes --package @playwright/cli playwright-cli)
else
  echo "Error: neither playwright-cli nor npx is available on PATH." >&2
  exit 1
fi

if [[ "${has_session_flag}" != "true" && -n "${PLAYWRIGHT_CLI_SESSION:-}" ]]; then
  cmd+=("-s=${PLAYWRIGHT_CLI_SESSION}")
fi
cmd+=("$@")

exec "${cmd[@]}"
