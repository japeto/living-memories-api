# feat: Add display_name to auth responses and profile endpoint

## Summary
The mobile app requires the `display_name` in the login response to greet the user. This plan updates the authentication flow to return `display_name` upon login/refresh and adds a `/me` endpoint to fetch user profile details.

## Scope
- Update `LoginResponse` schema.
- Update `auth/repository.py` to select `display_name`.
- Update `auth/service.py` to include `display_name` in auth responses.
- Add `GET /auth/me` endpoint to return the current user's profile.
- Update `test_auth.py` mocks and tests to cover these changes.

## Files to Create / Modify
| File | Action | Description |
|------|--------|-------------|
| `app/features/auth/schemas.py` | Modify | Add `display_name` to `LoginResponse`. Add new `UserProfileResponse` schema. |
| `app/features/auth/repository.py` | Modify | Update `get_user_by_email` to return `display_name`. Add new `get_user_by_id` method. |
| `app/features/auth/service.py` | Modify | Read `display_name` from DB results in `login` and `refresh` to populate `LoginResponse`. Add `get_user_profile` method. |
| `app/features/auth/router.py` | Modify | Add `GET /me` endpoint. |
| `tests/features/test_auth.py` | Modify | Update mock return values for DB queries to include `display_name`. Adapt `test_refresh` to handle two DB queries. Add tests for `GET /me`. |

## Data Contracts (Pydantic Schemas)
```python
# In app/features/auth/schemas.py

class LoginResponse(BaseModel):
    user_id: str
    display_name: str
    authenticated: bool
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"

class UserProfileResponse(BaseModel):
    user_id: str
    email: EmailStr
    display_name: str
```

## Business Logic / Change Description
1. **Schema Updates**:
   - `LoginResponse` will require `display_name`.
   - Add `UserProfileResponse`.
2. **Repository Layer**:
   - `get_user_by_email`: modify the Supabase `select()` to include `display_name`.
   - Add `get_user_by_id(user_id: str)`: query `users` table filtering by `id`, returning `id, email, display_name`.
3. **Service Layer**:
   - `login`: extract `display_name` from the fetched user dictionary and pass it to `LoginResponse`.
   - `refresh`: after validating the refresh token and extracting `user_id`, call `self._repository.get_user_by_id(user_id)` to get the user's `display_name` to construct the `LoginResponse`. Raise 404/503 if user retrieval fails.
   - Add `get_user_profile`: fetches user by ID using the repository, raises 404 if not found, and returns `UserProfileResponse`.
4. **Router Layer**:
   - Add `@router.get("/me")` using `CurrentUserDep` to get the authenticated user ID and delegate to `service.get_user_profile(user_id)`.
5. **Testing**:
   - Update `supabase_mock.table.return_value.execute.return_value.data` in existing tests to include `"display_name": "Test User"`.
   - For `refresh` tests, because `refresh` now invokes Supabase twice (once for the token, once for the user profile), configure `side_effect` on the mock to return sequentially different values, or mock the `get_user_by_id` repository call directly if `side_effect` is too brittle.
   - Add a test for `GET /api/v1/auth/me`.

## External Integrations
- Queries to Supabase will now pull additional columns. No new tables or integrations are required.

## Acceptance Criteria
- [ ] `pre-commit run --files <changed files>` → zero violations
- [ ] `pytest tests/features/test_auth.py` → all tests pass
- [ ] `LoginResponse` includes `display_name` properly on both `/login` and `/refresh`.
- [ ] `GET /api/v1/auth/me` requires authentication and returns the correct profile.

## Open Questions / Risk Alerts
- **Test Fragility**: The current `test_auth.py` mocks `supabase` generically. The `refresh` endpoint will now require sequential DB mocks. Consider advising the QA agent (`lm_qa`) to patch the `AuthRepository` methods instead for simpler tests if `supabase_mock` side-effects become unmanageable.
