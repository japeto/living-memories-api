#!/usr/bin/env python3
r"""
pre-commit hook: rejects .env secrets files from being committed.
.env.example is explicitly allowed and never blocked.

The `files` pattern in .pre-commit-config.yaml already filters to only
files matching '^\.env(?!\.example)', so this script always exits 1.
"""

import sys

print(
    "COMMIT REJECTED — attempt to commit a secrets file detected.\n"
    "  Never commit .env files — they may contain API keys and credentials.\n"
    "  Use .env.example to document required variables instead."
)
sys.exit(1)
