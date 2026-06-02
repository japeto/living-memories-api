# feat: Implement Registration Endpoint (HU1)

## Summary
Implement the `/auth/register` endpoint in the `living-memories-api` to allow new users to register. The endpoint will validate the required fields (name, email, pin, conditions), check for existing emails, hash the PIN securely, and store the user in the Supabase database.

## Scope
- **In scope**: Create Pydantic schemas for registration. Add password hashing utility (`passlib` + `bcrypt`). Implement `create_user` method in `AuthRepository` and `register` method in `AuthService`. Add `POST /auth/register` route.
- **Out of scope**: JWT generation or session tokens (if authentication uses a different mechanism, though we will align the response with the current login flow).

## Files to Create / Modify
| File | Action | Description |
|------|--------|-------------|
| `pyproject.toml` | Modify | Add `passlib`, `bcrypt`, and `email-validator` (for `EmailStr`) to dependencies. |
| `app/core/security.py` | Create | Add `get_password_hash` and `verify_password` utilities. |
| `app/features/auth/schemas.py` | Modify | Add `RegisterRequest` and `RegisterResponse` schemas. |
| `app/features/auth/repository.py` | Modify | Add `create_user` method. |
| `app/features/auth/service.py` | Modify | Add `register` method handling business logic and hashing. |
| `app/features/auth/router.py` | Modify | Add `@router.post("/register")` endpoint. |

## Data Contracts (Pydantic Schemas)
```python
from pydantic import BaseModel, Field, EmailStr, field_validator

class RegisterRequest(BaseModel):
    display_name: Annotated[str, Field(min_length=2)]
    email: EmailStr
    pin: Annotated[str, Field(pattern=r"^\d{4}$")]
    conditions_accepted: bool

    @field_validator("conditions_accepted")
    def must_accept_conditions(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Debes aceptar las condiciones")
        return v

class RegisterResponse(BaseModel):
    user_id: str
    email: EmailStr
    display_name: str
    authenticated: bool
```

## Business Logic / Change Description
1. **Security**: Introduce `passlib` with `bcrypt` to hash the 4-digit PIN securely before storing it. 
2. **Repository**: Create `create_user(email, display_name, pin_hash)` to insert into the Supabase `users` table. If the email already exists, Supabase will throw a unique constraint violation which we will catch.
3. **Service**: 
   - Validate that `conditions_accepted` is `True`.
   - Hash the PIN.
   - Call the repository to create the user. If a conflict occurs, raise `HTTPException(409, "Email already registered")`.
4. **Router**: Expose `POST /auth/register` returning status `201 Created`.

## External Integrations
- **Supabase**: Insert into `users` table.

## Acceptance Criteria
- [ ] `pre-commit run --files <changed files>` → zero violations.
- [ ] Missing required fields return `422 Unprocessable Entity`.
- [ ] Invalid email or PIN format returns `422`.
- [ ] `conditions_accepted=false` returns `422`.
- [ ] Existing email returns `409 Conflict`.
- [ ] Successful registration returns `201 Created` with user data and inserts into DB with a hashed PIN.
