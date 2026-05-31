#!/usr/bin/env python3
"""
commit-msg hook: validates that the commit message follows the Conventional
Commits specification and includes the required Co-authored-by trailers.

Invoked by pre-commit at the commit-msg stage with the path to the commit
message file as the first argument.
"""

import re
import sys

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CONVENTIONAL_COMMIT_RE = re.compile(
    r"^(feat|fix|hotfix|chore|docs|refactor|test|build|ci|perf|style)" r"(\([^)]+\))?!?:\s.{1,72}",
)

REQUIRED_TRAILER = "Co-authored-by: Iader E. Garcia G. <iadergg@gmail.com>"

VALID_TYPES = (
    "feat",
    "fix",
    "hotfix",
    "chore",
    "docs",
    "refactor",
    "test",
    "build",
    "ci",
    "perf",
    "style",
)

# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate(msg: str) -> list[str]:
    """Return a list of error strings; empty list means the message is valid."""
    errors: list[str] = []
    lines = msg.splitlines()

    if not lines:
        return ["Commit message is empty."]

    subject = lines[0]

    # Skip automatically generated merge and revert commits.
    if subject.startswith(("Merge ", "Revert ")):
        return []

    # --- Subject line ---
    if not CONVENTIONAL_COMMIT_RE.match(subject):
        errors.append(
            f"Subject line does not follow Conventional Commits format.\n"
            f"  Expected : <type>(<scope>): <description>  (max 72 chars)\n"
            f"  Got      : {subject}\n"
            f"  Valid types: {', '.join(VALID_TYPES)}"
        )

    # --- Co-authored-by trailer ---
    if REQUIRED_TRAILER not in msg:
        errors.append(
            f"Missing required Co-authored-by trailer.\n"
            f"  Required : {REQUIRED_TRAILER}\n"
            f"  Tip      : Add it after a blank line at the end of the message."
        )

    return errors


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: validate_commit_msg.py <commit-msg-file>")
        return 1

    commit_msg_file = sys.argv[1]

    try:
        with open(commit_msg_file, encoding="utf-8") as f:
            msg = f.read()
    except OSError as exc:
        print(f"ERROR: Could not read commit message file: {exc}")
        return 1

    errors = validate(msg)

    if errors:
        print("COMMIT REJECTED — fix the following issues:\n")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}\n")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
