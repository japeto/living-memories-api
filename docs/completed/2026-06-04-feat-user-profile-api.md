# Implementation Plan: User Profile Feature

## Summary
Currently, the user profile endpoint is located within the `auth` feature (`GET /auth/me`) and only returns basic fields (`id`, `email`, `display_name`). To provide a complete user profile without mocks while adhering to the Vertical Slice Architecture, we will extract the profile logic into a dedicated `profile` feature slice and extend the `users` table to include `full_name` and `avatar_url`.

## Scope
- Create a new Supabase database migration to add `full_name` and `avatar_url` columns to the `users` table.
- Create a new `profile` feature slice (`app/features/profile/`) containing its own router, service, repository, and schemas.
- Move and rename the existing `GET /auth/me` endpoint to `GET /profile/me`.
- Update the data contracts to include the new fields.
- Ensure all FastAPI conventions (e.g., `Annotated` dependencies, explicit return types, `async` handlers) are strictly followed.

## Files to Modify
- **`supabase/migrations/0007_add_profile_fields.sql`** (Create): Add `full_name` (text, nullable) and `avatar_url` (text, nullable) to the `users` table.
- **`app/features/profile/schemas.py`** (Create): Define `UserProfileResponse`.
- **`app/features/profile/repository.py`** (Create): Implement `ProfileRepository` with async Supabase queries.
- **`app/features/profile/service.py`** (Create): Implement `ProfileService` with mapping and error handling.
- **`app/features/profile/router.py`** (Create): Implement the `profile` APIRouter and the `GET /me` endpoint.
- **`app/features/auth/schemas.py`** (Modify): Remove `UserProfileResponse`.
- **`app/features/auth/service.py`** (Modify): Remove `get_user_profile` method.
- **`app/features/auth/router.py`** (Modify): Remove `GET /me` endpoint.
- **`app/core/router.py`** (Modify): Include the new `profile` router in `api_router`.

## Data Contracts
Contracts will use Pydantic v2 with explicit validation:

```python
from pydantic import BaseModel, EmailStr

class UserProfileResponse(BaseModel):
    user_id: str
    email: EmailStr
    display_name: str
    full_name: str | None = None
    avatar_url: str | None = None
```

## Business Logic
1. **Dependency Injection**: Services and repositories will be injected using FastAPI's `Annotated` and `Depends`. The router will use `CurrentUserDep` to authenticate requests and extract the current `user_id`.
2. **Database Queries**: `ProfileRepository.get_user_profile(user_id: str)` will query Supabase asynchronously:
   ```python
   await self._client.table("users").select("id, email, display_name, full_name, avatar_url").eq("id", user_id).limit(1).execute()
   ```
3. **Error Handling**: `ProfileService` will catch `postgrest.exceptions.APIError`, `httpx.ConnectError`, and `TimeoutException` and raise a `503 Service Unavailable` error. If no user is found, it raises a `404 Not Found`.
4. **Async-first**: All route handlers, service methods, and repository methods will use `async def`.

## Acceptance Criteria
- `GET /api/v1/profile/me` successfully returns a `200 OK` response with `user_id`, `email`, `display_name`, `full_name`, and `avatar_url`.
- The `auth` feature slice no longer contains profile-fetching logic or endpoints (`GET /api/v1/auth/me` returns `404`).
- The implementation completely avoids mocks and fetches real data from Supabase.
- Code conforms strictly to project conventions (`uv`, `ruff`, explicit return types, `Annotated`).
