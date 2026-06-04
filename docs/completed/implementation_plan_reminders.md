# Implementation Plan: Reminders Feature

## 1. Context & Objectives
Implement the "Reminders" feature (Recordatorios). A memory can generate multiple reminders using AI (Gemini). We will create a new vertical slice for Reminders, update the existing Gemini analysis prompt, update the `memories` service to save the parsed reminders, and expose the required endpoints.

## 2. Database Schema (Supabase)
Create a new table `reminders` linked to the `memories` table.

```sql
CREATE TABLE reminders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    memory_id UUID REFERENCES memories(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    due_date TIMESTAMP WITH TIME ZONE NOT NULL,
    description TEXT,
    is_done BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```
*(Optional but recommended: Drop `reminder_text` from the `memories` table to avoid redundancy).*

## 3. New Vertical Slice: `app/features/reminders/`

### `schemas.py`
- Create `ReminderResponse` reflecting the table columns.
- Create `ReminderUpdateRequest` containing `is_done: bool`.

### `repository.py`
- Create `RemindersRepository`.
- **`get_reminders(user_id: str)`**: Fetch reminders by joining the `memories` table to filter by `user_id`.
  `client.table("reminders").select("*, memories!inner(user_id)").eq("memories.user_id", user_id)`
  *Security Note*: Clean the `memories` key from the data before returning.
- **`update_reminder(reminder_id: str, data: dict, user_id: str)`**: **Critical:** Perform an application-level tenancy check (since the API bypasses RLS with service keys). Verify that the reminder belongs to a memory owned by `user_id` before performing the update.
- **`create_reminders(reminders_data: list[dict])`**: Bulk insert multiple reminders.

### `service.py`
- Create `RemindersService` with methods mapping to the repository (`get_reminders`, `update_reminder`, `create_reminders`).
- Format the AI outputs to dictionary representations before calling `create_reminders`.

### `router.py`
- Expose `GET /reminders` using `user_id: CurrentUserDep` to list user's reminders.
- Expose `PATCH /reminders/{reminder_id}` to update `is_done`, passing `user_id` down to the service/repository to enforce ownership.

## 4. Updates to `app/features/ai_analysis/`

### `gemini_service.py`
- Update `PROMPT_TEMPLATE`.
- Add context for the current date/time to help the model calculate relative dates: `La fecha y hora actuales son: {current_time}`.
- Request the model to extract an array of reminders instead of a single string.
  ```json
  "reminders": [
    {
      "title": "...",
      "due_date": "YYYY-MM-DDTHH:MM:SSZ",
      "description": "..."
    }
  ]
  ```
- Pass `datetime.now().isoformat()` into the prompt during `.evaluate_memory(...)`.

## 5. Updates to `app/features/memories/`

### `schemas.py`
- Create `GeminiReminder(BaseModel)` and add `reminders: list[GeminiReminder] = []` to `GeminiEvaluationResult`.
- Remove `reminder_text` from `GeminiEvaluationResult` and `MemoryResponse`.

### `service.py`
- Inject `RemindersService` into the `MemoriesService` constructor.
- Update `get_memories_service` factory function with `reminders_service: RemindersService = Depends(get_reminders_service)`.
- In `evaluate_and_update_memory`: 
  - Remove `reminder_text` from the `update_data` dictionary.
  - If `result.reminders` has items, call `self.reminders_service.create_reminders(memory_id, result.reminders)` to save them in the database.

## 6. Core Router Registration

### `app/core/router.py`
- Import and register the new `reminders` router: `api_router.include_router(reminders_router)`.

## 7. Open Questions / Risk Alerts
- **Tenancy Enforcement:** We rely on application-level checks to ensure a user only queries or modifies their own reminders. The implementation must strictly verify `memories.user_id` in `update_reminder`.
- **Date Standardization:** The model should output ISO 8601 strict timestamps (`due_date`). Validation in `GeminiReminder` might throw errors if the AI hallucinates a bad format. We should handle parsing errors gracefully (e.g., skip invalid reminders or log errors without crashing the whole memory processing task).
