#!/usr/bin/env python3
"""Stand-alone acceptance probe for EDGA-7969."""
from __future__ import annotations

import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent


def check(path: Path) -> None:
    if not path.exists():
        raise RuntimeError(f"Missing: {path}")
    print(f"[OK] {path}")


def main() -> int:
    check(SKILL_ROOT / "SKILL.md")
    check(SKILL_ROOT / "lib" / "edgeless_guard.py")
    check(SKILL_ROOT / "schemas" / "policy.schema.json")
    check(SKILL_ROOT / "bin" / "edgeless-guard")
    check(SKILL_ROOT / "references" / "policies" / "hipaa.json")
    check(SKILL_ROOT / "references" / "policies" / "sox.json")
    check(SKILL_ROOT / "references" / "policies" / "finra.json")
    check(SKILL_ROOT / "references" / "policies" / "eu-ai-act.json")
    check(SKILL_ROOT / "tests" / "test_edgeless_guard.py")

    test = sys.executable, str(SKILL_ROOT / "tests" / "test_edgeless_guard.py"), "-v"
    import subprocess
    proc = subprocess.run(test, capture_output=True, text=True, cwd=str(SKILL_ROOT))
    print(proc.stdout)
    if proc.returncode != 0:
        print(proc.stderr)
        return 1

    print("EDGA-7969 acceptance complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
