#!/usr/bin/env python3
"""
verify-canonical-vault.py - Verify vault is at canonical location

Checks for common wrong vault locations and reports drift.
Part of vault-taxonomy-enforcement skill.
"""

from pathlib import Path
import sys

WRONG_LOCATIONS = [
    Path.home() / "claude-vault",
    Path.home() / "Projects",
    Path.home() / "claude-projects" / "claude-vault" / "claude-vault",  # Nested bug
]

CORRECT_VAULT = Path.home() / "claude-projects" / "claude-vault"
CORRECT_PROJECTS = Path.home() / "claude-projects" / "projects"

def check_wrong_locations():
    """Check if wrong vault locations exist."""
    issues = []
    
    for wrong in WRONG_LOCATIONS:
        if wrong.exists():
            items = len(list(wrong.rglob('*'))) if wrong.is_dir() else 0
            issues.append(f"❌ Wrong location exists: {wrong} ({items} items)")
    
    return issues

def check_correct_locations():
    """Verify correct locations exist."""
    issues = []
    
    if not CORRECT_VAULT.exists():
        issues.append(f"❌ Correct vault missing: {CORRECT_VAULT}")
    else:
        items = len(list(CORRECT_VAULT.rglob('*')))
        print(f"✅ Correct vault: {CORRECT_VAULT} ({items} items)")
    
    if not CORRECT_PROJECTS.exists():
        issues.append(f"⚠️  Projects dir missing: {CORRECT_PROJECTS}")
    else:
        items = len(list(CORRECT_PROJECTS.iterdir()))
        print(f"✅ Correct projects: {CORRECT_PROJECTS} ({items} items)")
    
    return issues

def check_taxonomy_collisions():
    """Check for numbered folder collisions."""
    issues = []
    
    if not CORRECT_VAULT.exists():
        return issues
    
    prefixes = {}
    for item in CORRECT_VAULT.iterdir():
        if item.is_dir() and item.name[:2].isdigit():
            prefix = item.name[:2]
            if prefix not in prefixes:
                prefixes[prefix] = []
            prefixes[prefix].append(item.name)
    
    for prefix, folders in prefixes.items():
        if len(folders) > 1:
            issues.append(f"❌ Collision {prefix}-*: {', '.join(folders)}")
    
    return issues

def main():
    print("=" * 60)
    print("VAULT CANONICAL LOCATION VERIFICATION")
    print("=" * 60)
    
    wrong_issues = check_wrong_locations()
    if wrong_issues:
        print("\n🚨 WRONG LOCATIONS DETECTED:")
        for issue in wrong_issues:
            print(f"   {issue}")
        print("\n→ Run vault-taxonomy-enforcement skill to migrate")
    else:
        print("\n✅ No wrong locations detected")
    
    correct_issues = check_correct_locations()
    if correct_issues:
        print("\n🚨 CORRECT LOCATION ISSUES:")
        for issue in correct_issues:
            print(f"   {issue}")
    
    collision_issues = check_taxonomy_collisions()
    if collision_issues:
        print("\n🚨 TAXONOMY COLLISIONS:")
        for issue in collision_issues:
            print(f"   {issue}")
        print("\n→ Run validate-taxonomy.py --fix or resolve manually")
    else:
        print("\n✅ No taxonomy collisions")
    
    print("\n" + "=" * 60)
    
    total_issues = len(wrong_issues) + len(correct_issues) + len(collision_issues)
    if total_issues == 0:
        print("✅ ALL CHECKS PASSED")
        return 0
    else:
        print(f"❌ {total_issues} ISSUE(S) FOUND")
        return 1

if __name__ == "__main__":
    sys.exit(main())
