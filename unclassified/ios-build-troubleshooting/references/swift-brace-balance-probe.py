#!/usr/bin/env python3
"""
String-aware brace balancer for Swift source files.
Counts { / } while ignoring string literals and // comments.
Reports net balance and last unmatched scope opener.
Usage: python swift-brace-balance-probe.py <path/to/file.swift>
"""
import sys

def check_brace_balance(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    balance = 0
    in_string = False
    string_char = None
    in_comment = False
    last_opener_line = None

    for i, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n")
        j = 0
        while j < len(line):
            ch = line[j]

            if in_comment:
                # Nothing matters until end of line
                j += 1
                continue

            if in_string:
                if ch == "\\" and j + 1 < len(line):
                    j += 2
                    continue
                if ch == string_char:
                    in_string = False
                    string_char = None
                j += 1
                continue

            if ch == "/" and j + 1 < len(line) and line[j + 1] == "/":
                in_comment = True
                j += 2
                continue

            if ch in ('"', "'"):
                in_string = True
                string_char = ch
                j += 1
                continue

            if ch == "{" :
                balance += 1
                last_opener_line = i
            elif ch == "}" :
                balance -= 1

            j += 1

        in_comment = False  # comment ends at newline

    return {
        "balance": balance,
        "last_opener_line": last_opener_line,
        "lines": len(lines),
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <file.swift>")
        sys.exit(1)

    result = check_brace_balance(sys.argv[1])
    print(f"Lines: {result['lines']}")
    print(f"Net brace balance: {result['balance']} (+ means unclosed openers)")
    print(f"Last unmatched scope opener: line {result['last_opener_line']}")
    if result["balance"] != 0:
        print("DIAGNOSIS: Brace mismatch detected. Check nesting around the last opener.")
        sys.exit(1)
    else:
        print("OK: Braces are balanced.")
        sys.exit(0)
