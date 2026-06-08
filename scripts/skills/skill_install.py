#!/usr/bin/env python3
"""
skill_install.py

Install skills into the local skills directories from:
    - GitHub repos (raw or git clone)
    - Local file paths
    - Generic git URLs

Usage:
    python skill_install.py --source <url|path> --skill <name> [--target-dir PATH]
    python skill_install.py --source <url|path> --all [--target-dir PATH]

Examples:
    python skill_install.py --source https://github.com/edgeless/skills --skill incident-response
    python skill_install.py --source ~/Downloads/skills --skill my-local-skill
    python skill_install.py --source git@github.com:edgeless/skills.git --skill research
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
DEFAULT_TARGETS = [
    Path.home() / ".hermes" / "skills",
    Path.home() / ".Codex" / "skills",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_github_url(source: str) -> tuple[str, str] | None:
    """Parse a GitHub URL into (owner, repo)."""
    m = re.match(r"https?://github\.com/([^/]+)/([^/]+)/?.*", source)
    if m:
        return m.group(1), m.group(2).replace(".git", "")
    m = re.match(r"git@github\.com:([^/]+)/([^/]+)\.git", source)
    if m:
        return m.group(1), m.group(2)
    return None


def fetch_github_skill(owner: str, repo: str, skill_name: str) -> dict[str, Any] | None:
    """Fetch a single skill from a GitHub repo via raw API."""
    import urllib.request
    base_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main"
    # Try to fetch the skill directory listing via manifest or heuristic
    manifest_url = f"{base_url}/manifest.json"
    try:
        with urllib.request.urlopen(manifest_url, timeout=10) as resp:  # noqa: S310
            manifest = json.loads(resp.read().decode())
    except Exception:
        manifest = None

    if manifest and skill_name in manifest.get("skills", {}):
        info = manifest["skills"][skill_name]
        path = info.get("path", f"{info.get('domain', 'unclassified')}/{skill_name}")
    else:
        # Heuristic: try common paths
        for domain in ["creative", "devops", "research", "product", "tooling", "observability", "ingestion", "knowledge", "security", "system", "external", "unclassified"]:
            path = f"{domain}/{skill_name}"
            test_url = f"{base_url}/{path}/SKILL.md"
            try:
                with urllib.request.urlopen(test_url, timeout=10) as resp:  # noqa: S310
                    if resp.status == 200:
                        break
            except Exception:
                continue
        else:
            return None

    # Download skill files
    files: dict[str, str] = {}
    for filename in ("SKILL.md", "skill.md"):
        url = f"{base_url}/{path}/{filename}"
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:  # noqa: S310
                files[filename] = resp.read().decode("utf-8")
                break
        except Exception:
            continue
    if not files:
        return None

    # Attempt to download scripts/, references/, assets/ by listing via GitHub API (tree)
    # For simplicity, we return metadata and let the caller clone if needed
    return {
        "source": "github",
        "owner": owner,
        "repo": repo,
        "path": path,
        "files": files,
        "needs_clone": True,
    }


def clone_skill(source: str, skill_name: str, dest: Path) -> bool:
    """Clone a skill directory from a git repo into dest."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        result = subprocess.run(
            ["git", "clone", "--depth", "1", source, str(tmp_path)],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            print(f"Error: git clone failed: {result.stderr}")
            return False

        # Try to find skill directory
        candidates = [
            tmp_path / skill_name,
            tmp_path / "unclassified" / skill_name,
            tmp_path / "system" / skill_name,
        ]
        for domain in ["creative", "devops", "research", "product", "tooling", "observability", "ingestion", "knowledge", "security", "system", "external"]:
            candidates.append(tmp_path / domain / skill_name)

        for c in candidates:
            if c.exists() and c.is_dir():
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(c, dest)
                return True

        # Try manifest
        manifest_path = tmp_path / "manifest.json"
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text())
            info = manifest.get("skills", {}).get(skill_name)
            if info:
                src = tmp_path / info.get("path", skill_name)
                if src.exists():
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(src, dest)
                    return True

        print(f"Error: skill '{skill_name}' not found in cloned repo")
        return False


def install_from_path(source_path: Path, skill_name: str, dest: Path) -> bool:
    """Install from a local path."""
    src = source_path / skill_name
    # Only accept src if it looks like a skill directory (has SKILL.md or skill.md)
    if src.exists() and not any((src / c).exists() for c in ("SKILL.md", "skill.md")):
        src = None  # type: ignore[assignment]
    if not src or not src.exists():
        # Try subdirectories
        for domain in ["creative", "devops", "research", "product", "tooling", "observability", "ingestion", "knowledge", "security", "system", "external", "unclassified"]:
            candidate = source_path / domain / skill_name
            if candidate.exists():
                src = candidate
                break
    if not src or not src.exists():
        print(f"Error: skill '{skill_name}' not found in {source_path}")
        return False
    if dest.exists():
        shutil.rmtree(dest)
    if src.is_dir():
        shutil.copytree(src, dest)
    else:
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
    return True


def install_skill(source: str, skill_name: str, target_dir: Path | None = None, all_skills: bool = False) -> int:
    """Install a skill. Returns 0 on success, 1 on failure."""
    # Determine target
    if target_dir:
        targets = [target_dir]
    else:
        targets = [t for t in DEFAULT_TARGETS if t.exists()]
        if not targets:
            # Create default target
            target = DEFAULT_TARGETS[0]
            target.mkdir(parents=True, exist_ok=True)
            targets = [target]

    install_target = targets[0]

    if all_skills:
        # Install all skills from source
        if not source.startswith("http") and not source.startswith("git@"):
            source_path = Path(source)
            if not source_path.exists():
                print(f"Error: source path does not exist: {source_path}")
                return 1
            count = 0
            for item in source_path.iterdir():
                if item.is_dir() and not item.name.startswith("."):
                    dest = install_target / item.name
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(item, dest)
                    count += 1
            print(f"✅ Installed {count} skills to {install_target}")
            return 0
        else:
            print("Error: --all only supported for local paths")
            return 1

    dest = install_target / skill_name
    dest.parent.mkdir(parents=True, exist_ok=True)

    if source.startswith("http") or source.startswith("git@"):
        gh = parse_github_url(source)
        if gh:
            owner, repo = gh
            meta = fetch_github_skill(owner, repo, skill_name)
            if meta and meta.get("needs_clone"):
                return 0 if clone_skill(source, skill_name, dest) else 1
        return 0 if clone_skill(source, skill_name, dest) else 1
    else:
        source_path = Path(source)
        if not source_path.exists():
            print(f"Error: source path does not exist: {source_path}")
            return 1
        return 0 if install_from_path(source_path, skill_name, dest) else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Install skills from GitHub, local paths, or git URLs")
    parser.add_argument("--source", required=True, help="GitHub URL, git URL, or local path")
    parser.add_argument("--skill", help="Skill name to install")
    parser.add_argument("--all", action="store_true", help="Install all skills from source (local only)")
    parser.add_argument("--target-dir", type=Path, help="Override target directory")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be installed")
    args = parser.parse_args()

    if not args.all and not args.skill:
        parser.error("--skill is required unless --all is used")

    if args.dry_run:
        print(f"Would install skill '{args.skill}' from '{args.source}' into local skills directory")
        return 0

    return install_skill(args.source, args.skill, args.target_dir, args.all)


if __name__ == "__main__":
    sys.exit(main())
