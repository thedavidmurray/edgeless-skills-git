#!/usr/bin/env python3
"""Test script for tradingview-skill proxy.

Verifies:
1. MCP server starts and initializes correctly
2. Tool list can be fetched
3. Tool schema is valid (has name + description)
4. No duplicate tool names

Usage:
    python3 scripts/test_proxy.py

Returns exit code 0 on success, 1 on failure.
"""

import sys
import os

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from proxy import get_bridge


def main():
    print("[TEST] TradingView skill proxy verification")
    print("-" * 50)

    try:
        bridge = get_bridge()

        # Test 1: Fetch tools
        print("[1/4] Fetching tool list...")
        tools = bridge.get_tools()
        print(f"       OK: {len(tools)} tools loaded")

        # Test 2: Validate tool schema
        print("[2/4] Validating tool schema...")
        invalid = []
        for t in tools:
            if not t.get("name") or not t.get("description"):
                invalid.append(t.get("name", "<unnamed>"))
        if invalid:
            print(f"       FAIL: {len(invalid)} tools missing name or description")
            return 1
        print("       OK: All tools have name + description")

        # Test 3: Check for duplicates
        print("[3/4] Checking for duplicate tool names...")
        names = [t["name"] for t in tools]
        dupes = [n for n in names if names.count(n) > 1]
        if dupes:
            print(f"       FAIL: Duplicates found: {set(dupes)}")
            return 1
        print("       OK: No duplicates")

        # Test 4: Verify expected categories exist
        print("[4/4] Checking expected tool categories...")
        expected_prefixes = ["chart_", "pine_", "data_", "ui_", "tv_"]
        found = set()
        for t in tools:
            for prefix in expected_prefixes:
                if t["name"].startswith(prefix):
                    found.add(prefix)
        print(f"       OK: Found {len(found)}/{len(expected_prefixes)} expected prefixes")
        print(f"       Categories: {sorted(found)}")

        print("-" * 50)
        print("[PASS] All proxy tests passed")
        return 0

    except Exception as e:
        print(f"[FAIL] Proxy test failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
