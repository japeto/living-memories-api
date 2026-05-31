# chore: initialize project structure

## Summary
The project has no runnable state. This task establishes the complete initial
structure so the app boots, tests run, and a new developer can clone and start
working with a single setup command. Designed to land as the first meaningful
push to main, from which develop is created.

## Scope
All foundational files: dependency management, package markers, config fix,
router architecture fix, stub feature recreation, test scaffold, env example,
and README. No business logic is implemented.

## Git Strategy
- Work branch: `chore/initialize-project-structure` (from current state)
- Target: `main` (first push)
- After merge: create `develop` from `main`
- All future feature work branches from `develop`

## Files to Create / Modify

| File | Action | Description |
|------|--------|-------------|
| `pyproject.toml` | Create | Project metadata, FastAPI entrypoint, Ruff + pytest config |
| `requirements.txt` | Create | Pinned runtime dependencies |
| `requirements-dev.txt` | Create | Pinned dev/test dependencies |
| `.env.example` | Create | Document required env vars |
| `README.md` | Create | Setup, run, and test instructions |
| `app/__init__.py` | Create | Package marker |
| `app/core/__init__.py` | Create | Package marker |
| `app/features/__init__.py` | Create | Package marker |
| `app/features/auth/__init__.py` | Create | Package marker |
| `app/features/audio_management/__init__.py` | Create | Package marker |
| `app/features/audio_management/router.py` | Create | Recreate lost stub router |
| `app/features/ai_analysis/__init__.py` | Create | Package marker |
| `app/features/ai_analysis/router.py` | Create | Recreate lost stub router |
| `app/core/config.py` | Modify | Upgrade to Pydantic v2 SettingsConfigDict style |
| `app/core/router.py` | Create | Central v1 APIRouter; includes all feature routers |
| `main.py` | Modify | Use core router; fix language on root endpoint |
| `tests/__init__.py` | Create | Package marker |
| `tests/conftest.py` | Create | AsyncClient fixture and app setup |
| `tests/features/__init__.py` | Create | Package marker |
| `tests/features/test_auth.py` | Create | Placeholder test to verify pytest runs |
| `tests/features/test_audio_management.py` | Create | Placeholder test |
| `tests/features/test_ai_analysis.py` | Create | Placeholder test |

## Change Description

### Dependency management
- `pyproject.toml`: project metadata + FastAPI CLI entrypoint (`main:app`) +
  Ruff config (line-length 100, py312, select E/F/I/N/W/UP) +
  pytest config (asyncio_mode="auto", testpaths=["tests"])
- `requirements.txt`: pin runtime deps (fastapi, pydantic, pydantic-settings,
  uvicorn, httpx, python-dotenv, python-multipart)
- `requirements-dev.txt`: pin dev deps (pytest, pytest-asyncio, pytest-mock,
  pytest-cov, ruff)

### Config fix (Pydantic v2)
Replace `class Config: case_sensitive = True` with
`model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")`.
Add `SUPABASE_URL`, `SUPABASE_KEY` as optional string fields (populated later).

### Router architecture fix (per FastAPI skill)
Remove `prefix=settings.API_V1_STR` from every `include_router()` call in `main.py`.
Create `app/core/router.py` — a central `APIRouter(prefix="/api/v1")` that
includes all feature routers. `main.py` includes only this one router.
Feature routers already carry their own prefix and tags — no changes needed there.

### main.py fix
- Include `api_router` from `app/core/router.py` instead of three separate calls
- Root endpoint: change response message to English

### Feature stub recreation
Recreate the two lost router files with the same stub structure as `auth/router.py`.

### Test scaffold
`conftest.py` sets up an `AsyncClient` fixture against the FastAPI app.
Placeholder tests assert `True` so `pytest` reports green from day one.

## Acceptance Criteria
- [ ] `fastapi dev` starts without ImportError or warnings
- [ ] `GET /` returns 200
- [ ] `GET /api/v1/openapi.json` returns 200 (all routes registered)
- [ ] `python -m pytest tests/ -v` → all tests pass (green)
- [ ] `ruff check .` → zero violations
- [ ] A new developer can run: `python -m venv .venv && pip install -r requirements.txt -r requirements-dev.txt` and the app boots

## Open Questions / Risk Alerts
- Supabase and AI provider credentials are not yet available — Settings fields
  will be Optional[str] = None for now and validated when features are implemented.
