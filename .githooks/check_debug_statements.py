#!/usr/bin/env python3
"""
pre-commit hook: rejects debug statements in app/ source files.

Catches: print(), breakpoint(), pdb.set_trace(), import pdb, import ipdb.
Test files (tests/) are intentionally excluded via .pre-commit-config.yaml
`files` pattern — print() in tests is acceptable.

Invoked by pre-commit with the list of staged files as arguments.
"""

import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Patterns that indicate a debug statement
# ---------------------------------------------------------------------------

DEBUG_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bprint\s*\("),
    re.compile(r"\bbreakpoint\s*\("),
    re.compile(r"\bpdb\.set_trace\s*\("),
    re.compile(r"^\s*import pdb\b"),
    re.compile(r"^\s*import ipdb\b"),
    re.compile(r"\bipdb\.set_trace\s*\("),
]

# ---------------------------------------------------------------------------
# Checker
# ---------------------------------------------------------------------------


def check_file(path: Path) -> list[tuple[int, str]]:
    """Return a list of (line_number, line_content) tuples for each violation."""
    violations: list[tuple[int, str]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []

    for lineno, line in enumerate(lines, 1):
        if any(pattern.search(line) for pattern in DEBUG_PATTERNS):
            violations.append((lineno, line.rstrip()))

    return violations


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> int:
    files = [Path(p) for p in sys.argv[1:]]
    found_any = False

    for path in files:
        violations = check_file(path)
        if violations:
            found_any = True
            for lineno, line in violations:
                print(f"  {path}:{lineno}: {line}")

    if found_any:
        print(
            "\nCOMMIT REJECTED — debug statements found in app/ code.\n"
            "Remove or replace them with proper logging before committing."
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
