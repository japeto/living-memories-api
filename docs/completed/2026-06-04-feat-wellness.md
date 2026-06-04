# feat: Wellness Feature (Bienestar)

## Summary
Implement the new `wellness` (Bienestar) vertical slice to aggregate user memories and return the weekly wellness data. This data will be consumed by the frontend to render the mood chart ("Ánimo de la semana") and topic distribution ("De qué hablas más").

## Scope
- Create a new `wellness` feature in `app/features/wellness/`.
- Aggregate the existing memories created during the current week to calculate daily mood levels and topic percentages.
- Integrate the new router into the central `api_router`.
- Note: This PR will point to the `dev` branch and use the existing PR template as per project conventions.

## Files to Create / Modify
| File | Action | Description |
|------|--------|-------------|
| `app/features/wellness/__init__.py` | Create | Empty init file to mark the directory as a package. |
| `app/features/wellness/schemas.py` | Create | Pydantic v2 data contracts for the `WellnessResponse`, matching the mobile `useWellnessViewModel` structure (`week`, `moods`, `topics`). |
| `app/features/wellness/repository.py` | Create | `WellnessRepository` to fetch memories between specific start and end dates for a `user_id`. |
| `app/features/wellness/service.py` | Create | `WellnessService` with business logic to calculate current week dates, process mood heuristic values, and calculate topic percentages. |
| `app/features/wellness/router.py` | Create | FastAPI router exposing `GET /api/v1/wellness/current-week`. |
| `app/core/router.py` | Modify | Include the new `wellness_router` in the `api_router`. |

## Data Contracts (Pydantic Schemas)
**`app/features/wellness/schemas.py`**
```python
from pydantic import BaseModel, Field

class MoodEntry(BaseModel):
    day: str = Field(..., description="Day initial, e.g., 'L', 'M', 'M'")
    level: float = Field(..., description="Mood level between 0.0 and 1.0")
    label: str = Field(..., description="Mood label, e.g., 'Alegría', 'Nostalgia', or 'Sin registro'")

class TopicEntry(BaseModel):
    name: str = Field(..., description="Topic name")
    percentage: int = Field(..., description="Percentage of this topic in the week")

class WellnessResponse(BaseModel):
    week: str = Field(..., description="Formatted string of the current week")
    moods: list[MoodEntry] = Field(..., description="List of 7 mood entries for the week")
    topics: list[TopicEntry] = Field(..., description="List of top topics with their percentages")
```

## Business Logic / Change Description
1. **Repository Layer (`app/features/wellness/repository.py`)**:
   - `get_memories_for_date_range(user_id: str, start_date: datetime, end_date: datetime)`: Calls Supabase `client.table("memories").select("created_at, mood, topic")` with `.gte` and `.lte` filters for the date range, returning only necessary fields.

2. **Service Layer (`app/features/wellness/service.py`)**:
   - Calculate `start_of_week` (Monday at 00:00:00) and `end_of_week` (Sunday at 23:59:59) in UTC.
   - Format `week` string in Spanish (e.g., "Del 12 al 18 de Octubre").
   - Call repository to fetch memories for the calculated range.
   - **Mood Aggregation**:
     - Pre-fill an array of 7 items (L, M, M, J, V, S, D) with `level=0.0` and `label="Sin registro"`.
     - Iterate through memories, map the `created_at` date to a weekday index (0-6).
     - Map the `mood` string to a numerical value using a simple heuristic dictionary (e.g., "Alegría": 0.8, "Tranquilo": 0.6, "Cansancio": 0.5, "Nostalgia": 0.4, "Tristeza": 0.2). If multiple memories exist on the same day, take the highest value or the most recent.
   - **Topic Aggregation**:
     - Extract `topic` strings, count frequencies, calculate percentage over total topics.
     - Select top N topics (e.g., top 4) and map them to `TopicEntry`.

3. **Router Layer (`app/features/wellness/router.py`)**:
   - Expose `GET /current-week` using `@router.get("/current-week", response_model=WellnessResponse)`.
   - Inject `CurrentUserDep` and `WellnessService`.
   - Ensure `app/core/router.py` correctly registers this new router.

## External Integrations
- Supabase: Uses existing Supabase async client to fetch records. No schema changes are required as `memories` table already contains `mood` and `topic` columns.

## Acceptance Criteria
- [ ] `WellnessResponse` structure exactly matches what the frontend `useWellnessViewModel.ts` expects (`week`, `moods`, `topics`).
- [ ] Router does not contain business logic; logic resides purely in `WellnessService`.
- [ ] Unit tests pass and `pre-commit run --all-files` results in zero violations.
- [ ] PR correctly points to `dev` and includes the project's PR template.

## Open Questions / Risk Alerts
- **Mood Values Mappings**: The NLP prompt in Gemini (memories feature) returns dynamic mood strings. The static dictionary mapped in the service (`Alegría`, `Nostalgia`, etc.) should safely fallback to a default level (e.g., 0.5) and label for unmapped moods.
- **Timezone**: Date range calculations use UTC. If the user's local timezone is significantly offset, a late Sunday memory could be counted as Monday of the next week. For a future iteration, we may want to pass the user's timezone from the mobile app as a query parameter.
