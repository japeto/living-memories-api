# fix: Handle user timezone for memories and reminders

## Summary
Currently, the AI analysis runs using the server's UTC time. When a user records a memory saying "remind me tomorrow at 8 AM", Gemini interprets "tomorrow at 8 AM" relative to UTC, leading to incorrect reminder due dates being saved. To fix this, we need to capture the user's timezone on the mobile client, pass it to the backend during memory upload, and inject it into the Gemini prompt so the LLM calculates and returns local, offset-aware timestamps.

## Scope
- **In scope**:
  - `living-memories-mobile`: Fetch device timezone and send it in the memory upload request.
  - `living-memories-api`: Accept `time_zone` in the upload endpoint, resolve the user's local time, and inject it into the Gemini prompt. 
  - `living-memories-api`: Force Gemini to output timezone-aware ISO 8601 strings (e.g., `YYYY-MM-DDTHH:MM:SS±HH:MM`).
- **Out of scope**:
  - Modifying Supabase table definitions (Postgres `timestamptz` automatically converts aware datetimes to UTC).
  - Changing how reminders are displayed on the frontend (they are already localized correctly via `Intl.DateTimeFormat`).

## Files to Create / Modify

| Repository | File | Action | Description |
|------------|------|--------|-------------|
| **Mobile** | `src/domain/memories/repositories/IMemoryRepository.ts` | Modify | Add `timeZone: string` to the `uploadMemory` signature. |
| **Mobile** | `src/data/repositories/MemoryRepository.ts` | Modify | Update implementation of `uploadMemory` to include `timeZone`. |
| **Mobile** | `src/data/repositories/MockMemoryRepository.ts` | Modify | Update mock implementation of `uploadMemory` to match interface. |
| **Mobile** | `src/data/network/memoriesApiClient.ts` | Modify | Add `time_zone` to the POST body payload in `uploadMemory`. |
| **Mobile** | `src/domain/memories/useCases/RecordMemoryUseCase.ts` | Modify | Retrieve timezone via `Intl.DateTimeFormat().resolvedOptions().timeZone` and pass it to the repository. |
| **Mobile** | `src/data/__tests__/*`, `src/domain/__tests__/*` | Modify | Update relevant test files to match the new `uploadMemory` signature. |
| **API** | `app/features/memories/schemas.py` | Modify | Add `time_zone: str = "UTC"` to `MemoryCreateRequest`. |
| **API** | `app/features/memories/router.py` | Modify | Pass `request.time_zone` to the background task `service.evaluate_and_update_memory`. |
| **API** | `app/features/memories/service.py` | Modify | Update `evaluate_and_update_memory` signature to receive `time_zone` and pass it to `gemini_service.evaluate_memory`. |
| **API** | `app/features/ai_analysis/gemini_service.py` | Modify | Parse `time_zone` to calculate aware `current_time`. Update `PROMPT_TEMPLATE` to inject the timezone and request `due_date` with an offset (`YYYY-MM-DDTHH:MM:SS±HH:MM`). |

## Data Contracts (Pydantic Schemas / DTOs)

**API (`MemoryCreateRequest`)**
```python
class MemoryCreateRequest(BaseModel):
    text: str
    time_zone: str = "UTC"
```

**Mobile (`memoriesApiClient.ts`)**
```typescript
// The POST body of uploadMemory will now include:
{
  "text": string,
  "time_zone": string
}
```

## Business Logic / Change Description

1. **Mobile - Fetch and send timezone:**
   - In `RecordMemoryUseCase.ts`, execute `const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;`.
   - Pass this `timeZone` down through `MemoryRepository.ts` to `memoriesApiClient.ts`.
   - `memoriesApiClient.ts` adds it to the JSON payload.

2. **API - Receive timezone and process in background:**
   - The `/memories/upload` endpoint parses `time_zone` and pushes it to `MemoriesService.evaluate_and_update_memory` as a background task.
   - `MemoriesService` relays it to `GeminiService.evaluate_memory`.

3. **API - AI Prompt Injection:**
   - In `GeminiService`, use the built-in `zoneinfo.ZoneInfo(time_zone)` to get the user's timezone. Fallback to `"UTC"` if parsing fails.
   - Get the user's localized current time: `current_time = datetime.now(user_tz).isoformat()`.
   - Update `PROMPT_TEMPLATE`:
     - Tell Gemini: `La fecha y hora local actuales del usuario son: {current_time} (Zona horaria: {time_zone})`
     - Ask Gemini to output the reminder `due_date` as `YYYY-MM-DDTHH:MM:SS±HH:MM` instead of ending with `Z`.
   - Pydantic's `datetime` parser (in `GeminiReminder`) will automatically parse this into a timezone-aware datetime.
   - When saving to Postgres (`RemindersService`), `.isoformat()` will stringify the aware datetime correctly, allowing Supabase's `timestamptz` column to store it as absolute UTC time.

## Acceptance Criteria
- [ ] Memory upload endpoint accepts `time_zone` without errors.
- [ ] Mobile app retrieves the device's exact IANA timezone string and sends it when recording a memory.
- [ ] `gemini_service.py` generates `current_time` correctly localized and prompts the LLM to return offset-aware timestamps.
- [ ] Reminders created from memories are saved with the correct UTC time corresponding to the user's request.
- [ ] Pull Requests target the `develop` branch for both `living-memories-api` and `living-memories-mobile`.

## Open Questions / Risk Alerts
- Does the LLM consistently respect the `±HH:MM` format requirement? If the LLM sometimes drops the offset, Pydantic will parse it as a naive datetime, which might cause Supabase to treat it as UTC. We will use strong prompting to enforce the ISO 8601 offset format.
