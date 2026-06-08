#!/usr/bin/env python3
"""
skill_sync.py

Mirror skills from local directories (~/.hermes/skills/ and ~/.Codex/skills/)
into the edgeless-skills git repository, organized by domain.

Usage:
    python skill_sync.py [--commit] [--push] [--repo PATH] [--source PATH ...]

Features:
    - Copies skill directories (SKILL.md, scripts/, references/, assets/)
    - Generates manifest.json with skill metadata and checksums
    - Auto-commits with a descriptive message
    - Optionally pushes to origin
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
DEFAULT_SOURCES = [
    Path.home() / ".hermes" / "skills",
    Path.home() / ".Codex" / "skills",
]

DEFAULT_REPO = Path.home() / "claude-projects" / "edgeless-skills"

DOMAINS = [
    "creative",
    "devops",
    "research",
    "product",
    "tooling",
    "observability",
    "ingestion",
    "knowledge",
    "security",
    "system",
    "external",
    "unclassified",
]

# Files/dirs to exclude from sync
EXCLUDE = {".git", "__pycache__", ".DS_Store", ".archive", ".disabled", ".hub", ".curator_backups", ".usage.json", ".usage.json.lock", ".bundled_manifest", ".curator_state", ".system", "*.bak"}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_frontmatter(path: Path) -> dict[str, Any] | None:
    """Parse YAML frontmatter from a markdown file."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        return yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return None


def sha256_dir(path: Path) -> str:
    """Compute a combined SHA256 hash of all files in a directory."""
    h = hashlib.sha256()
    for fp in sorted(path.rglob("*")):
        if fp.is_file() and not any(part.startswith(".") for part in fp.relative_to(path).parts):
            if fp.suffix == ".bak":
                continue
            h.update(fp.relative_to(path).as_posix().encode())
            h.update(fp.read_bytes())
    return h.hexdigest()[:16]


def get_skill_name(skill_dir: Path) -> str:
    """Return skill name from frontmatter or directory name."""
    for candidate in ("SKILL.md", "skill.md"):
        fm_path = skill_dir / candidate
        if fm_path.exists():
            fm = parse_frontmatter(fm_path)
            if fm and "name" in fm:
                return fm["name"]
    return skill_dir.name


def get_skill_domain(skill_dir: Path) -> str:
    """Return domain from frontmatter or infer from directory name."""
    for candidate in ("SKILL.md", "skill.md"):
        fm_path = skill_dir / candidate
        if fm_path.exists():
            fm = parse_frontmatter(fm_path)
            if fm:
                domain = fm.get("domain", "")
                if domain:
                    return domain
                metadata = fm.get("metadata", {})
                tags = [t.lower() for t in metadata.get("tags", [])]
                for d in DOMAINS:
                    if d in tags or d in skill_dir.name.lower():
                        return d
    return "unclassified"


def copy_skill(source_dir: Path, target_dir: Path) -> bool:
    """Copy a skill directory into the repo, skipping excluded files."""
    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    copied = False
    for item in source_dir.iterdir():
        if item.name in EXCLUDE:
            continue
        dest = target_dir / item.name
        if item.is_dir():
            shutil.copytree(item, dest, ignore=shutil.ignore_patterns(*EXCLUDE))
        else:
            shutil.copy2(item, dest)
        copied = True
    return copied


def run_git(cmd: list[str], cwd: Path) -> str:
    """Run a git command and return stdout."""
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(cmd)} failed: {result.stderr}")
    return result.stdout.strip()


def generate_manifest(repo_dir: Path) -> dict[str, Any]:
    """Generate manifest.json from all skills in the repo."""
    manifest: dict[str, Any] = {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "domains": {},
        "skills": {},
    }
    for domain in DOMAINS:
        domain_dir = repo_dir / domain
        if not domain_dir.exists():
            continue
        skills_in_domain: list[str] = []
        for skill_dir in sorted(domain_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            skill_name = get_skill_name(skill_dir)
            skills_in_domain.append(skill_name)
            manifest["skills"][skill_name] = {
                "domain": domain,
                "path": f"{domain}/{skill_name}",
                "checksum": sha256_dir(skill_dir),
                "has_scripts": (skill_dir / "scripts").is_dir(),
                "has_references": (skill_dir / "references").is_dir(),
                "has_assets": (skill_dir / "assets").is_dir(),
            }
        if skills_in_domain:
            manifest["domains"][domain] = skills_in_domain
    return manifest


def sync_skills(repo_dir: Path, sources: list[Path]) -> list[str]:
    """Sync skills from sources into repo. Returns list of synced skill names."""
    synced: list[str] = []
    for source in sources:
        if not source.exists():
            print(f"Warning: source directory does not exist: {source}")
            continue
        for item in sorted(source.iterdir()):
            if not item.is_dir():
                continue
            if item.name in EXCLUDE or item.name.startswith("."):
                continue
            # Only sync if it contains a skill file
            if not any((item / c).exists() for c in ("SKILL.md", "skill.md")):
                continue
            skill_name = get_skill_name(item)
            domain = get_skill_domain(item)
            target_dir = repo_dir / domain / skill_name
            if copy_skill(item, target_dir):
                synced.append(skill_name)
    return synced


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync local skills to the edgeless-skills repo")
    parser.add_argument("--repo", type=Path, default=DEFAULT_REPO, help="Path to edgeless-skills repo")
    parser.add_argument("--source", action="append", type=Path, help="Extra source directories")
    parser.add_argument("--commit", action="store_true", help="Auto-commit changes")
    parser.add_argument("--push", action="store_true", help="Push after commit")
    parser.add_argument("--message", default="", help="Custom commit message suffix")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    repo_dir = args.repo.resolve()
    if not repo_dir.exists():
        print(f"Error: repo directory does not exist: {repo_dir}")
        return 1

    sources = list(DEFAULT_SOURCES)
    if args.source:
        sources.extend(args.source)

    # Ensure git repo
    git_dir = repo_dir / ".git"
    if not git_dir.exists():
        print("Info: initializing git repository...")
        run_git(["git", "init", "-b", "main"], cwd=repo_dir)
        run_git(["git", "config", "user.email", "edgeless@localhost"], cwd=repo_dir)
        run_git(["git", "config", "user.name", "Edgeless Swarm"], cwd=repo_dir)

    synced = sync_skills(repo_dir, sources)
    manifest = generate_manifest(repo_dir)
    manifest_path = repo_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    if args.verbose:
        print(f"Synced {len(synced)} skills:")
        for s in synced:
            print(f"  - {s}")

    # Check for changes
    status = run_git(["git", "status", "--short"], cwd=repo_dir)
    if not status:
        print("✅ No changes to commit.")
        return 0

    if args.commit:
        run_git(["git", "add", "-A"], cwd=repo_dir)
        count = len(synced)
        msg = f"sync: {count} skills from local directories"
        if args.message:
            msg += f" - {args.message}"
        msg += f"\n\nSkills: {', '.join(synced) if synced else 'none'}"
        run_git(["git", "commit", "-m", msg], cwd=repo_dir)
        print(f"✅ Committed: {msg.splitlines()[0]}")
        if args.push:
            run_git(["git", "push", "origin", "main"], cwd=repo_dir)
            print("✅ Pushed to origin/main")
    else:
        print(f"👀 Changes detected (use --commit to commit):\n{status}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
