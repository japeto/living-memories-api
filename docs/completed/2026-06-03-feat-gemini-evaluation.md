# feat: AI Evaluation with Gemini (Backend & Mobile)

## Summary
Integrate Gemini via `google-genai` to evaluate audio transcriptions into structured topics and moods (Valence-Arousal), returning a short title and reminder. Uses FastAPI `BackgroundTasks` for asynchronous processing to avoid Render timeouts, and polling on the mobile app to update the UI when evaluation completes.

## Scope
- In scope: Database schema update (status, title), `GeminiService` implementation, FastAPI BackgroundTask routing, React Native polling, UI updates.
- Out of scope: Audio transcription logic (assumed already done), Push Notifications (we use polling).

## Files to Create / Modify

### Backend (living-memories-api)
| File | Action | Description |
|------|--------|-------------|
| `supabase/migrations/0004_add_memory_status.sql` | CREATE | Adds `status` and `title` to `memories` table |
| `app/core/config.py` | MODIFY | Add `GEMINI_API_KEY` |
| `app/features/ai_analysis/gemini_service.py` | CREATE | Evaluates text using `google-genai` SDK and Structured Outputs |
| `app/features/memories/schemas.py` | MODIFY | Add `status`, `title` fields to models |
| `app/features/memories/repository.py` | MODIFY | Add `update_memory` method |
| `app/features/memories/service.py` | MODIFY | Move processing to background task using Gemini |
| `app/features/memories/router.py` | MODIFY | Inject `BackgroundTasks` |

### Mobile (living-memories-mobile)
| File | Action | Description |
|------|--------|-------------|
| `src/domain/entities/Memory.ts` | MODIFY | Add `status` and `title` |
| `src/data/dto/MemoryDTO.ts` | MODIFY | Update data mappers |
| `src/presentation/viewmodels/useMemoriesViewModel.ts` | MODIFY | Polling mechanism for `status === 'processing'` |
| `src/presentation/screens/HomeScreen.tsx` | MODIFY | UI handling for loading states |

## Prompt Design (Spanish)
```text
Eres un asistente experto en psicología geriátrica y análisis de lenguaje.
Analiza la siguiente transcripción de voz de un adulto mayor y extrae información estructurada.
Clasifica el tema (topic) en una de las siguientes opciones exactas:
- Familia y Amigos
- Salud y Bienestar
- Recuerdos de Juventud
- Actividades y Rutina
- Reflexiones y Consejos

Clasifica el estado de ánimo (mood) en una de las siguientes opciones exactas:
- Entusiasmado
- Alegre
- Relajado
- Tranquilo
- Nostálgico
- Triste
- Ansioso / Preocupado
- Frustrado / Enojado

Además, genera un título (title) corto que resuma la memoria, y si el usuario menciona algo que deba recordar (una cita médica, comprar algo, llamar a alguien), extráelo en reminder_text. Si no hay nada que recordar, déjalo nulo.

Transcripción: {text}
```

## Data Contracts (Pydantic Schemas)
- Add `status: str` and `title: str | None` to `MemoryResponse`.
- Create `GeminiEvaluationResult` model matching the prompt structure.

## Acceptance Criteria
- [ ] Local Supabase migrations run successfully.
- [ ] Creating memory returns 202 Accepted and `status='processing'`.
- [ ] Polling updates memory to `status='completed'` with `mood`, `topic`, `title`.
- [ ] Mobile app correctly displays loading state and updates.

## Open Questions / Risk Alerts
- Requires local `.env` updates for `GEMINI_API_KEY`.
