# chore: create .gitignore

## Summary
The repo has no .gitignore. This creates a comprehensive one covering Python,
FastAPI tooling (uv, Ruff), pytest, and project-specific entries required by the team.

## Scope
Create `.gitignore` at the repo root. No source files are modified.

## Files to Create / Modify
| File | Action | Description |
|------|--------|-------------|
| `.gitignore` | Create | Root-level gitignore |

## Change Description

### Python standard
- `__pycache__/`, `*.py[cod]`, `*.pyo`
- `*.egg-info/`, `dist/`, `build/`, `*.egg`

### Virtual environment
- `.venv/` — explicitly requested
- `venv/`, `env/` — common alternatives

### FastAPI tooling (from .agents/skills/fastapi)
- `.uv/` — uv package manager cache
- `.ruff_cache/` — Ruff linter cache

### Testing & coverage
- `.pytest_cache/`
- `.coverage`, `htmlcov/`, `coverage.xml`

### Secrets & local config
- `.env`, `.env.*` (except `.env.example`)

### Project-specific (explicitly requested)
- `.agents/` — full folder excluded
- `.claude/skills/lm-writer/` — only the writer skill; the rest of .claude stays tracked

### IDE & OS
- `.idea/`, `.vscode/`, `*.swp`, `*.swo`
- `.DS_Store`, `Thumbs.db`

## Acceptance Criteria
- [ ] `git check-ignore -v .venv` → matched
- [ ] `git check-ignore -v .agents` → matched
- [ ] `git check-ignore -v .claude/skills/lm-writer` → matched
- [ ] `.claude/skills/lm-architect` is NOT ignored (still tracked)
- [ ] `git status` shows no untracked noise files
