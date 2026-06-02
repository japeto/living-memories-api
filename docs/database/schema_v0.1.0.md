# Database Schema v0.1.0 — Mi Recuerdo Vivo

Authoritative reference for the initial PostgreSQL/Supabase schema. The DDL lives in
[`supabase/migrations/0001_init_v0.1.0.sql`](../../supabase/migrations/0001_init_v0.1.0.sql);
this document explains the model and the decisions behind it.

## Scope
Covers the three v0.1.0 slices:

| Slice | User Stories | Tables |
|-------|--------------|--------|
| `auth` | US-6 | `users` |
| `audio_management` | US-10, US-13 | `audio_recordings` |
| `ai_analysis` | US-11, US-12 | `transcriptions`, `ai_analyses` |

## Entity-Relationship Overview
```
users (1) ──< (N) audio_recordings (1) ──── (0..1) transcriptions
                                    (1) ──── (0..1) ai_analyses
```
`audio_recordings` is the central entity: one row per voice note. Its transcription and
AI analysis are 1-to-1 children, each enforced by a `UNIQUE` constraint on `recording_id`.

## Tables

### `users`
| Column | Type | Notes |
|--------|------|-------|
| `id` | `uuid` PK | `gen_random_uuid()` |
| `email` | `citext` | **Unique**, case-insensitive — the login identifier |
| `display_name` | `text` | Who the person is; shown in the app |
| `pin_hash` | `text` | Constant-time hash of the 4-digit PIN (set in US-6) |
| `created_at` | `timestamptz` | `now()` |

Signup creates the row with `(email, display_name, pin)`. Login uses `(email, pin)`.

### `audio_recordings`
| Column | Type | Notes |
|--------|------|-------|
| `id` | `uuid` PK | `gen_random_uuid()` |
| `user_id` | `uuid` FK → `users.id` | `ON DELETE CASCADE` |
| `storage_path` | `text` | Path to the object in Supabase Storage |
| `mime_type` | `text` | e.g. `audio/m4a`, `audio/wav` |
| `duration_seconds` | `numeric(7,2)` | Nullable (client may omit it) |
| `status` | `recording_status` | Lifecycle enum (see below) |
| `recorded_at` | `timestamptz` | When the note was recorded on-device |
| `created_at` | `timestamptz` | `now()` |
| `updated_at` | `timestamptz` | Maintained by the `set_updated_at` trigger |

Index `idx_audio_recordings_user_recent (user_id, created_at desc)` serves
`GET /api/v1/audios/` (a user's recordings, most recent first).

### `transcriptions`
| Column | Type | Notes |
|--------|------|-------|
| `id` | `uuid` PK | `gen_random_uuid()` |
| `recording_id` | `uuid` FK → `audio_recordings.id` | **Unique**, `ON DELETE CASCADE` |
| `text` | `text` | STT output |
| `language` | `text` | Defaults to `es` |
| `created_at` | `timestamptz` | `now()` |

### `ai_analyses`
| Column | Type | Notes |
|--------|------|-------|
| `id` | `uuid` PK | `gen_random_uuid()` |
| `recording_id` | `uuid` FK → `audio_recordings.id` | **Unique**, `ON DELETE CASCADE` |
| `sentiment` | `sentiment_label` | `positive` / `neutral` / `negative` |
| `topic` | `text` + CHECK | `family` / `medical` / `leisure` / `finances` / `other` |
| `physical_state` | `physical_state` | `good` / `regular` / `poor`, nullable |
| `has_reminder` | `boolean` | Defaults to `false` |
| `reminder_at` | `timestamptz` | Nullable; required iff `has_reminder` is true |
| `reminder_text` | `text` | Nullable |
| `created_at` | `timestamptz` | `now()` |

`POST /api/v1/ai/classify` reads the stored transcription for `recording_id` and writes
the analysis. The `reminder_consistency` CHECK guarantees a reminder always carries a
timestamp and a non-reminder never does.

## Processing Lifecycle (`status`)
```
POST /api/v1/audios/        → pending
POST /api/v1/ai/transcribe  → transcribed
POST /api/v1/ai/classify    → analyzed
any failure                 → failed
```

## Design Decisions
- **Email as `citext`, unique** — case-insensitive uniqueness (`A@x.com` == `a@x.com`),
  the natural identifier for a human-typed login that works across devices.
- **Plural table names** — matches the Supabase/PostgREST convention and the existing
  `auth/repository.py` (`.table("users")`); also avoids the reserved word `user`.
- **`topic` as TEXT + CHECK, not an enum** — the topic taxonomy is expected to grow, and
  a CHECK constraint is cheaper to alter than a Postgres enum. `sentiment` and
  `physical_state` stay enums (stable sets).
- **Reminders stored inline on `ai_analyses`** — sufficient for v0.1.0. When US-4
  (reminder notifications) lands, a dedicated `reminders` table can be split out.
- **No RLS** — all access control lives in the FastAPI layer via the service-role key,
  which must never reach the mobile client.
- **`ON DELETE CASCADE`** throughout — deleting a user removes their recordings,
  transcriptions, and analyses.

## Applying the Migration
Run the DDL on a fresh Supabase project either via the Supabase CLI
(`supabase db push`) or by pasting `0001_init_v0.1.0.sql` into the SQL editor.
`pgcrypto` (for `gen_random_uuid()`) is enabled by default on Supabase; `citext` is
enabled by the migration itself.
