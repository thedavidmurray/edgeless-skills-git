#!/usr/bin/env python3
"""
session_auto_commit.py

Auto-commit hook for skill changes after sessions.

Intended to be called at the end of a session (e.g., from a shell hook,
Hermes post-session trigger, or cron job). It:

    1. Detects which skills were modified during the session
    2. Runs skill_frontmatter.py on changed skills
    3. Syncs to the edgeless-skills repo via skill_sync.py
    4. Commits with a session-aware message

Usage:
    python session_auto_commit.py [--session-id ID] [--repo PATH] [--sources PATH ...]

Environment:
    EDGELESS_SKILLS_REPO   — override default repo path
    EDGELESS_SESSION_ID    — session identifier for commit message
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
DEFAULT_REPO = Path.home() / "claude-projects" / "edgeless-skills"
DEFAULT_SOURCES = [
    Path.home() / ".hermes" / "skills",
    Path.home() / ".Codex" / "skills",
]

STATE_FILE = Path.home() / ".hermes" / "edgeless_skills_session_state.json"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sha256_dir(path: Path) -> str:
    """Compute a combined SHA256 hash of all files in a directory."""
    h = hashlib.sha256()
    for fp in sorted(path.rglob("*")):
        if fp.is_file() and not any(part.startswith(".") for part in fp.relative_to(path).parts):
            h.update(fp.relative_to(path).as_posix().encode())
            h.update(fp.read_bytes())
    return h.hexdigest()[:16]


def snapshot_skills(sources: list[Path]) -> dict[str, Any]:
    """Create a snapshot of skill hashes."""
    snapshot: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "skills": {},
    }
    for source in sources:
        if not source.exists():
            continue
        for item in source.iterdir():
            if not item.is_dir() or item.name.startswith("."):
                continue
            if not any((item / c).exists() for c in ("SKILL.md", "skill.md")):
                continue
            snapshot["skills"][item.name] = {
                "source": str(source),
                "hash": sha256_dir(item),
            }
    return snapshot


def load_state() -> dict[str, Any] | None:
    if not STATE_FILE.exists():
        return None
    try:
        return json.loads(STATE_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def save_state(state: dict[str, Any]) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def run_command(cmd: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{result.stderr}")
    return result.stdout.strip()


def find_changed_skills(old_state: dict[str, Any] | None, new_state: dict[str, Any]) -> list[str]:
    """Compare snapshots and return changed skill names."""
    if old_state is None:
        return list(new_state.get("skills", {}).keys())
    old_skills = old_state.get("skills", {})
    new_skills = new_state.get("skills", {})
    changed: list[str] = []
    for name, info in new_skills.items():
        if old_skills.get(name, {}).get("hash") != info.get("hash"):
            changed.append(name)
    for name in old_skills:
        if name not in new_skills:
            changed.append(name)
    return changed


def run_frontmatter(skills: list[str], sources: list[Path]) -> None:
    """Run frontmatter migration on changed skills."""
    script_dir = Path(__file__).parent.resolve()
    frontmatter_script = script_dir / "skill_frontmatter.py"
    if not frontmatter_script.exists():
        print(f"Warning: frontmatter script not found at {frontmatter_script}")
        return
    for source in sources:
        if not source.exists():
            continue
        for skill in skills:
            skill_dir = source / skill
            for candidate in ("SKILL.md", "skill.md"):
                path = skill_dir / candidate
                if path.exists():
                    run_command([sys.executable, str(frontmatter_script), "--source", str(source)])
                    break


def run_sync(repo_dir: Path, sources: list[Path], session_id: str) -> None:
    """Run sync script and commit."""
    script_dir = Path(__file__).parent.resolve()
    sync_script = script_dir / "skill_sync.py"
    if not sync_script.exists():
        print(f"Warning: sync script not found at {sync_script}")
        return
    cmd = [
        sys.executable, str(sync_script),
        "--repo", str(repo_dir),
        "--commit",
        "--message", f"session-auto-commit id={session_id}",
    ]
    for source in sources:
        cmd.extend(["--source", str(source)])
    run_command(cmd)


def main() -> int:
    parser = argparse.ArgumentParser(description="Auto-commit skill changes after sessions")
    parser.add_argument("--session-id", default=os.environ.get("EDGELESS_SESSION_ID", ""), help="Session identifier")
    parser.add_argument("--repo", type=Path, default=DEFAULT_REPO, help="Path to edgeless-skills repo")
    parser.add_argument("--source", action="append", type=Path, help="Extra source directories")
    parser.add_argument("--save-snapshot", action="store_true", help="Only save snapshot and exit")
    parser.add_argument("--diff", action="store_true", help="Show diff and exit without committing")
    args = parser.parse_args()

    sources = list(DEFAULT_SOURCES)
    if args.source:
        sources.extend(args.source)

    session_id = args.session_id or f"session-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"

    # Load previous state
    old_state = load_state()

    # Save current snapshot
    new_state = snapshot_skills(sources)
    save_state(new_state)

    if args.save_snapshot:
        print(f"✅ Snapshot saved for {len(new_state['skills'])} skills")
        return 0

    changed = find_changed_skills(old_state, new_state)
    if not changed:
        print("✅ No skill changes detected since last snapshot.")
        return 0

    print(f"📡 Skills changed: {', '.join(changed)}")

    if args.diff:
        print(f"Would auto-commit {len(changed)} skills (session {session_id})")
        return 0

    # Run frontmatter migration on changed skills
    run_frontmatter(changed, sources)

    # Sync and commit
    run_sync(args.repo, sources, session_id)
    print(f"✅ Auto-commit complete for session {session_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
