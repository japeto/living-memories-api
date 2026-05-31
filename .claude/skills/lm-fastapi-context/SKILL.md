---
name: lm-fastapi-context
description: Loads the official FastAPI conventions and best practices for the LivingMemories project. Inherited by lm_architect and lm_developer — invoke this skill at the start of any task involving FastAPI code design or implementation. Covers Annotated parameters, dependency injection, async vs sync, Pydantic v2 patterns, router conventions, and recommended tooling (uv, Ruff, SQLModel, HTTPX).
---

# lm-fastapi-context — FastAPI Conventions Context

ROLE: FastAPI Context Provider for the LivingMemories project
PURPOSE: This skill is a shared context layer inherited by lm_architect and lm_developer. It loads the authoritative FastAPI conventions so both agents design and implement code consistently.

## How to use this skill
When this skill is active, read the project's FastAPI skill file first to load the full, up-to-date conventions:

```
.agents/skills/fastapi/SKILL.md
```

That file is the single source of truth for FastAPI best practices. Everything below are **LivingMemories-specific additions and overrides** on top of it.

---

## LivingMemories-Specific FastAPI Conventions

### Always use `Annotated` — no exceptions
Following the official skill, all parameters, query values, path values, and dependencies use `Annotated`. This is enforced across all slices.

### `async def` for all route handlers
Per the FastAPI skill: use `async def` only when the logic inside is truly async. Since all our I/O goes through Supabase SDK and AI APIs (which are async), all route handlers in this project are `async def`.

### Dependency injection pattern for this project
Services and repositories are injected via `Annotated` + `Depends()` type aliases, defined at the top of each router file:

```python
from typing import Annotated
from fastapi import Depends
from app.features.audio.service import AudioService

AudioServiceDep = Annotated[AudioService, Depends(AudioService)]
```

### Router registration
Per the official skill, prefix and tags are declared on the `APIRouter`, not in `include_router()`. Routers are registered in `main.py`.

### Return types always declared
Every route handler declares an explicit return type annotation. This enables Pydantic serialization on the Rust side and ensures no sensitive fields leak through.

### Preferred libraries (from official FastAPI skill)
- **Package manager**: `uv`
- **Linter / formatter**: `Ruff`
- **Type checker**: `ty`
- **ORM**: `SQLModel` (preferred over raw SQLAlchemy)
- **HTTP client**: `HTTPX` (preferred over Requests)
- **Async utilities**: `Asyncer` (preferred over raw asyncio/AnyIO)

### Do NOT use
- `ORJSONResponse` or `UJSONResponse` (deprecated)
- `RootModel` (use `Annotated` + `Field` instead)
- `api_route()` with multiple methods (one function per HTTP operation)
- Ellipsis (`...`) as default for required fields
