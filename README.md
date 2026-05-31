# Mi Recuerdo Vivo — API

> FastAPI backend for the *Mi Recuerdo Vivo* mobile application.

**Mi Recuerdo Vivo** is a mobile application designed for elderly users. It uses AI to transform voice messages into a structured memory diary and generate periodic wellness summaries. This repository contains the REST API that powers the mobile clients.

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [AI-Augmented Development](#ai-augmented-development)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Running the API](#running-the-api)
- [Running Tests](#running-tests)
- [Code Quality](#code-quality)
- [Environment Variables](#environment-variables)
- [Git Conventions](#git-conventions)
- [Roadmap](#roadmap)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | [FastAPI](https://fastapi.tiangolo.com/) + Python 3.12 |
| Config | [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) (Pydantic v2) |
| Database / Storage | [Supabase](https://supabase.com/) (PostgreSQL + Object Storage) |
| Speech-to-Text | OpenAI Whisper |
| NLP / Classification | LLM (provider TBD) |
| HTTP Client | [HTTPX](https://www.python-httpx.org/) |
| Testing | pytest + pytest-asyncio + httpx AsyncClient |
| Linter / Formatter | [Ruff](https://docs.astral.sh/ruff/) |
| Package Manager | [uv](https://github.com/astral-sh/uv) (recommended) or pip |
| Runtime | WSL Ubuntu / Linux |

---

## Architecture

The project follows **Vertical Slice Architecture**: each feature is a self-contained module under `app/features/<feature>/`. Slices do not import from each other — shared concerns live in `app/core/`.

```
app/features/<feature>/
├── router.py       # HTTP layer — request/response only, no business logic
├── schemas.py      # Pydantic v2 input and output contracts
├── service.py      # Business logic — orchestrates the repository
└── repository.py   # Data access — Supabase SDK / SQLAlchemy
```

### Request flow

```
Client
  └─▶  main.py (FastAPI app)
         └─▶  app/core/router.py (central versioned APIRouter /api/v1)
                └─▶  app/features/<feature>/router.py
                       └─▶  service.py
                              └─▶  repository.py
                                     └─▶  Supabase / external APIs
```

### Key conventions

- All route handlers are `async def` — every I/O operation (Supabase, AI APIs) is async.
- `router.py` never calls `repository.py` directly — all business logic lives in `service.py`.
- All parameters and dependencies use `Annotated` style (no bare `Depends()`).
- Prefix and tags are declared on the `APIRouter`, not in `include_router()`.
- Pydantic v2 `BaseModel` with `model_config` for all schemas.
- `HTTPException` for all error responses — never return error dicts.

---

## AI-Augmented Development

This project is developed using a **multi-agent AI workflow** built on top of
[Claude Code](https://www.anthropic.com/claude-code). The ecosystem follows the
**Framework 4D de AI Fluency** (Dakan & Feller): Delegation, Description,
Discernment, and Diligence.

### Agent Ecosystem

| Agent | Role | Scope |
|---|---|---|
| `lm_architect` | Technical Architect | Reads the full repo, designs `implementation_plan.md`, never writes production code |
| `lm_developer` | FastAPI Developer | Implements code strictly from the approved plan |
| `lm_qa` | QA Engineer | Writes and runs pytest tests; reports pass/fail with coverage |
| `lm_git` | Git Operator | Creates branches, writes conventional commits, opens PRs; task-scoped staging only |
| `lm_writer` | Technical Writer *(optional)* | Logs sessions to the external knowledge base (Obsidian vault, in Spanish) |

### Human-on-the-Loop model

No agent writes code or commits changes without explicit human approval:

```
User describes task
  └─▶  lm_architect  →  implementation_plan.md  →  [human approves]
         └─▶  lm_developer  →  code  →  [human reviews]
                └─▶  lm_qa  →  tests  →  [human reviews]
                       └─▶  lm_git  →  branch + commit + PR
                              └─▶  (optional) lm_writer  →  knowledge base
```

Skills are stored as SKILL.md files in `.claude/skills/<agent-name>/`.  
The FastAPI conventions shared by all agents live in `.agents/skills/fastapi/SKILL.md`.

---

## Project Structure

```
living-memories-api/
├── main.py                        # FastAPI application entrypoint
├── pyproject.toml                 # Project metadata, Ruff and pytest config
├── requirements.txt               # Runtime dependencies
├── requirements-dev.txt           # Development and test dependencies
├── .env.example                   # Required environment variables (copy to .env)
├── implementation_plan.md         # Active task plan (written by lm_architect)
│
├── app/
│   ├── core/
│   │   ├── config.py              # pydantic-settings configuration
│   │   └── router.py              # Central versioned APIRouter (/api/v1)
│   └── features/
│       └── auth/                  # Authentication (US-6: 4-digit PIN)
│           └── router.py
│
├── tests/
│   ├── conftest.py                # AsyncClient fixture
│   └── features/
│       └── test_auth.py
│
├── docs/
│   └── completed/                 # Archived implementation plans (git mv, never deleted)
│
├── .agents/
│   └── skills/fastapi/SKILL.md   # Authoritative FastAPI conventions (read by agents)
│
└── .claude/
    └── skills/                    # Agent skill definitions (SKILL.md per agent)
        ├── lm-architect/
        ├── lm-developer/
        ├── lm-fastapi-context/
        ├── lm-git/
        ├── lm-qa/
        └── lm-writer/             # Excluded from Git (personal Obsidian paths)
```

---

## Getting Started

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- A Supabase project (required for features that use the database)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd living-memories-api

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux / macOS / WSL
# .venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt -r requirements-dev.txt

# Copy and fill in environment variables
cp .env.example .env
```

> **Note:** `SUPABASE_URL` and `SUPABASE_KEY` are optional at startup — the app boots
> without them. They will be validated when Supabase-dependent features are implemented.

---

## Running the API

```bash
# Development server with hot-reload (recommended)
fastapi dev main.py

# Production server
uvicorn main:app --host 0.0.0.0 --port 8000
```

Once running, open:

- **API root:** http://localhost:8000/
- **Interactive docs (Swagger):** http://localhost:8000/api/v1/docs *(when available)*
- **OpenAPI JSON:** http://localhost:8000/api/v1/openapi.json

---

## Running Tests

```bash
# Run all tests with verbose output
python -m pytest tests/ -v

# Run with coverage report
python -m pytest tests/ -v --cov=app --cov-report=term-missing
```

---

## Code Quality

```bash
# Lint and format check
ruff check .

# Auto-fix safe issues
ruff check . --fix

# Format
ruff format .
```

---

## Environment Variables

See `.env.example` for a full reference. Key variables:

| Variable | Required | Description |
|---|---|---|
| `PROJECT_NAME` | No | API title shown in docs (default: `Mi Recuerdo Vivo API`) |
| `VERSION` | No | API version (default: `0.1.0`) |
| `API_V1_STR` | No | API version prefix (default: `/api/v1`) |
| `SUPABASE_URL` | Future | Supabase project URL |
| `SUPABASE_KEY` | Future | Supabase anonymous key |

---

## Git Conventions

| Type | When to use |
|---|---|
| `feat` | New feature or endpoint |
| `fix` | Bug fix |
| `hotfix` | Critical production fix |
| `refactor` | Code change with no behavior change |
| `chore` | Tooling, dependencies, config |
| `test` | Tests only |
| `docs` | Documentation only |
| `style` | Formatting, linting (no logic change) |

**Commit format:** `<type>(<scope>): <short description in lowercase English>`

**Branch strategy:**
- `main` — production-ready code
- `develop` — integration branch; all feature branches merge here
- `feat/<name>`, `fix/<name>`, `chore/<name>` — short-lived work branches

PRs from feature branches → `develop`. Releases merge `develop` → `main`.

---

## Roadmap

| Status | Feature | User Story |
|---|---|---|
| 🔄 Stub | Auth | US-6: 4-digit PIN authentication |
| ⏳ Planned | Audio Management | US-10, US-13: voice upload and retrieval |
| ⏳ Planned | AI Analysis | US-11, US-12: transcription and NLP classification |
| ⏳ Planned | Memory Diary | Structured diary generation from audio entries |
| ⏳ Planned | Wellness Summary | Periodic AI-generated wellness reports |
