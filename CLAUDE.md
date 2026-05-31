# Living Memories API — Claude Code Project Context

## What is this project?
**Mi Recuerdo Vivo** is a mobile application for elderly users that uses AI to transform voice messages into a structured memory diary and wellness summaries.

This repository contains the **FastAPI backend** that exposes the REST API.

## Tech Stack
- **Framework**: FastAPI + Python 3.12
- **Architecture**: Vertical Slice Architecture (`app/features/<feature>/`)
- **Config**: pydantic-settings
- **Tests**: pytest + pytest-asyncio + httpx AsyncClient
- **DB/Storage**: Supabase (PostgreSQL + Storage)
- **AI**: Whisper (STT) + LLM (NLP/classification)
- **Environment**: WSL Ubuntu + `.venv`

## Repository Structure
```
living-memories-api/
├── main.py
├── app/
│   ├── core/config.py
│   └── features/
│       ├── auth/              # US-6: 4-digit PIN authentication
│       ├── audio_management/  # US-10, US-13
│       └── ai_analysis/       # US-11, US-12
└── tests/
```

## Language Rule (CRITICAL)
**Everything inside this repository must be written in technically correct English:**
- All code, comments, and docstrings
- All Markdown files (CLAUDE.md, implementation_plan.md, task.md, README.md)
- All skill instructions and agent plans
- PR titles, descriptions, and commit messages

The **only exception** is the external knowledge base (the Obsidian vault), which is the exclusive domain of the optional `lm_writer` skill and is written in Spanish. The vault path is documented inside the `lm-writer` skill, not here — other agents never touch it.

## Session Behavior: Human-on-the-Loop Model
Before writing any code, always:
1. Act as `lm_architect`: read the existing code, analyze context, and present a plan
2. Wait for explicit user approval
3. Act as `lm_developer`: implement following the approved plan
4. Act as `lm_qa`: write and run tests
5. Act as `lm_git`: create the branch and conventional commit
6. **(Optional)** Act as `lm_writer`: log the session in the external knowledge base (Spanish)

**Fallback when there is no `lm_writer` skill installed:** Not every developer uses an external knowledge base. If the `lm-writer` skill is unavailable, skip step 6 (external technical writing) entirely. The repo's `implementation_plan.md` (and its archive in `docs/completed/`) plus the PR are the single source of truth. The core flow — orchestrator coordinating architect → developer → qa → git — continues normally.

## Available Skills
| Skill | When to use |
|-------|-------------|
| `/lm-architect` | Technical analysis, implementation plan generation |
| `/lm-developer` | Endpoint, service, and repository implementation |
| `/lm-qa` | Writing and running pytest tests |
| `/lm-git` | Branches, conventional commits, Pull Requests |
| `/lm-writer` | *(Optional)* Session logging in the external knowledge base (Spanish) |

## Agent Security Boundaries
- **Only lm_developer** writes Python code in `app/`
- **Only lm_qa** writes tests in `tests/`
- **Only lm_git** performs Git operations (and archives the plan into `docs/completed/`)
- **Only lm_writer** writes to the external knowledge base (in Spanish) — if installed
- **lm_architect** is READ-ONLY on all repo files; only writes `implementation_plan.md`

## Implementation Plans Lifecycle
- The active plan lives at the repo root as `implementation_plan.md` (English), written by `lm_architect`.
- When the work is finished and the PR is created, `lm_git` archives it with `git mv` into `docs/completed/YYYY-MM-DD-<type>-<short-name>.md`.
- Plans are **never deleted** — archiving via `git mv` preserves traceability and Git history.
- If `lm_writer` is installed, a Spanish counterpart is kept in the external knowledge base; otherwise the repo plan is the only record.

## Code Conventions
- All I/O must be `async/await`
- Pydantic v2 for all schemas
- Full type hints on all functions
- Comments only for non-obvious WHY; never state what the code does
- Slice structure: `router.py → service.py → repository.py`

## Git Conventions
- Branches: `feat/`, `fix/`, `chore/`, `refactor/`, `test/` in kebab-case
- Commits: `<type>(<scope>): <short description in lowercase English>`
- PR titles and descriptions in English
- Communicate with the user in Spanish
