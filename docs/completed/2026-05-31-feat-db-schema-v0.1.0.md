# feat: Database schema design v0.1.0 (PostgreSQL / Supabase)

## Summary
Design and provision the initial PostgreSQL schema on Supabase for v0.1.0, covering the
three core slices: `auth` (US-6), `audio_management` (US-10, US-13), and `ai_analysis`
(US-11, US-12). The `audio_recordings` table is the central entity; transcription and AI
analysis hang off it via 1-to-1 foreign keys.

## Scope
**In scope:**
- Four tables: `users`, `audio_recordings`, `transcriptions`, `ai_analyses`.
- One SQL migration file applied through the Supabase SQL editor / CLI.
- Enum types and CHECK constraints for data integrity.
- Indexes required by the known query patterns (notably `GET /audios/`).
- An `updated_at` trigger for mutable rows.

**Out of scope (explicitly):**
- Row Level Security (RLS). Per decision, v0.1.0 uses the Supabase **service-role key**
  exclusively from the backend; PIN auth is handled in application code, not in Postgres.
- Reminders/wellness aggregation tables (US-4, US-8, US-9) — deferred to a later version.
  Reminder data extracted during classification is stored inline on `ai_analyses` for now.
- Supabase Storage bucket policy configuration (tracked separately in the audio slice task).
- ORM models (SQLModel). This project talks to Postgres through the `supabase-py` SDK
  (`.table().select()...`), not an ORM, so the schema is delivered as raw SQL DDL.

## Files to Create / Modify
| File | Action | Description |
|------|--------|-------------|
| `supabase/migrations/0001_init_v0.1.0.sql` | Create | Full DDL: citext extension, enum types, 4 tables, FKs, indexes, `updated_at` trigger. |
| `docs/database/schema_v0.1.0.md` | Create | Human-readable ER description + decisions, for repo traceability. |
| `app/features/auth/schemas.py` | Modify (later task) | `LoginRequest` switches from `user_id: UUID` to `email: EmailStr`. |
| `app/features/auth/repository.py` | Modify (later task) | `get_user` looks up by `email` instead of `id`; selects `email, pin_hash`. |
| `app/features/auth/service.py` | Modify (later task) | `login` keys off email; tweak the "Invalid credentials" path accordingly. |

> The three `auth` files already exist and assume UUID-based login. The email switch is
> noted here for traceability but is implemented in the auth (US-6) task by lm_developer,
> not in this schema-only change.

> Note: directory placement follows the Supabase CLI convention (`supabase/migrations/`).
> If the team is not using the Supabase CLI, the same SQL can be pasted into the SQL editor;
> the file remains the single source of truth either way.

## Database Schema (DDL)

```sql
-- ============================================================================
-- 0001_init_v0.1.0.sql — Mi Recuerdo Vivo — initial schema
-- ============================================================================

-- Enum types (stable, small value sets) ---------------------------------------
create type recording_status as enum ('pending', 'transcribed', 'analyzed', 'failed');
create type sentiment_label  as enum ('positive', 'neutral', 'negative');
create type physical_state   as enum ('good', 'regular', 'poor');

-- Case-insensitive text for emails (so 'A@x.com' == 'a@x.com' for uniqueness).
create extension if not exists citext;

-- users -----------------------------------------------------------------------
-- Self-registration (signup): the mobile app creates the row with (email,
-- display_name, pin). Login uses (email, pin) — email is the human-friendly,
-- multi-device login identifier. pin_hash is a constant-time password hash
-- (set in US-6). email is unique and case-insensitive (citext).
create table users (
    id           uuid primary key default gen_random_uuid(),
    email        citext not null unique,
    display_name text not null,
    pin_hash     text not null,
    created_at   timestamptz not null default now()
);

-- audio_recordings ------------------------------------------------------------
-- Central entity. One row per voice note. The audio binary lives in Supabase
-- Storage; storage_path points to it. status drives the processing lifecycle.
create table audio_recordings (
    id           uuid primary key default gen_random_uuid(),
    user_id      uuid not null references users (id) on delete cascade,
    storage_path text not null,
    mime_type    text not null,
    duration_seconds numeric(7, 2),
    status       recording_status not null default 'pending',
    recorded_at  timestamptz not null,
    created_at   timestamptz not null default now(),
    updated_at   timestamptz not null default now()
);

-- Drives GET /api/v1/audios/ : most recent first, scoped per user.
create index idx_audio_recordings_user_recent
    on audio_recordings (user_id, created_at desc);

-- transcriptions --------------------------------------------------------------
-- 1-to-1 with a recording (UNIQUE recording_id). Produced by POST /ai/transcribe.
create table transcriptions (
    id           uuid primary key default gen_random_uuid(),
    recording_id uuid not null unique references audio_recordings (id) on delete cascade,
    text         text not null,
    language     text not null default 'es',
    created_at   timestamptz not null default now()
);

-- ai_analyses -----------------------------------------------------------------
-- 1-to-1 with a recording (UNIQUE recording_id). Produced by POST /ai/classify,
-- which reads the stored transcription for that recording. topic is TEXT+CHECK
-- (not an enum) because the topic taxonomy is expected to grow.
create table ai_analyses (
    id             uuid primary key default gen_random_uuid(),
    recording_id   uuid not null unique references audio_recordings (id) on delete cascade,
    sentiment      sentiment_label not null,
    topic          text not null
                   check (topic in ('family', 'medical', 'leisure', 'finances', 'other')),
    physical_state physical_state,
    has_reminder   boolean not null default false,
    reminder_at    timestamptz,
    reminder_text  text,
    created_at     timestamptz not null default now(),
    -- A reminder must carry a timestamp; a non-reminder must not.
    constraint reminder_consistency check (
        (has_reminder is true  and reminder_at is not null) or
        (has_reminder is false and reminder_at is null)
    )
);

-- updated_at trigger for audio_recordings -------------------------------------
create or replace function set_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

create trigger trg_audio_recordings_updated_at
    before update on audio_recordings
    for each row execute function set_updated_at();
```

## Entity Relationships
```
users (1) ──< (N) audio_recordings (1) ──── (0..1) transcriptions
                                    (1) ──── (0..1) ai_analyses
```
- `users → audio_recordings`: one user has many recordings. `ON DELETE CASCADE`.
- `audio_recordings → transcriptions`: 1-to-1, enforced by `UNIQUE(recording_id)`.
- `audio_recordings → ai_analyses`: 1-to-1, enforced by `UNIQUE(recording_id)`.

## Processing Lifecycle (status field)
```
signup/upload  ─ POST /api/v1/audios/      → status = 'pending'
transcription  ─ POST /api/v1/ai/transcribe → status = 'transcribed'
classification ─ POST /api/v1/ai/classify   → status = 'analyzed'
any failure    ─                            → status = 'failed'
```

## Data Contracts (impact on Pydantic schemas)
These are delivered later by lm_developer per slice; listed here so the schema and the
contracts stay aligned:
- `auth`: `users` adds `email` (unique, citext — the login identifier), `display_name`
  (signup), and `created_at`. `LoginRequest` becomes `(email: EmailStr, pin)`; the
  repository looks up by `email`. Signup payload is `(email, display_name, pin)`.
- `audio_management`: response schema maps `audio_recordings` columns; `status` serializes
  as a string enum; `duration_seconds` is nullable.
- `ai_analysis`: `transcriptions` and `ai_analyses` map directly; `reminder_at` /
  `reminder_text` are nullable and only present when `has_reminder` is true.

## External Integrations
- **Supabase PostgreSQL**: schema `public`, accessed via the existing async client in
  `app/core/supabase.py` using the service-role key. No RLS in v0.1.0.
- **Supabase Storage**: `audio_recordings.storage_path` references the uploaded object;
  bucket creation/policy is handled in the audio_management implementation task, not here.
- `gen_random_uuid()` requires the `pgcrypto` extension, which is enabled by default on
  Supabase — no `create extension` needed.

## Acceptance Criteria
- [ ] `0001_init_v0.1.0.sql` runs cleanly on a fresh Supabase project with zero errors.
- [ ] Inserting two users with emails differing only in case (`A@x.com` / `a@x.com`) is
      rejected by the unique constraint on `email` (citext).
- [ ] Inserting an `ai_analyses` row with `has_reminder = true` and `reminder_at = null`
      is rejected by the `reminder_consistency` constraint.
- [ ] Deleting a `users` row cascades to its recordings, transcriptions, and analyses.
- [ ] `docs/database/schema_v0.1.0.md` documents the four tables and the decisions below.

## Open Questions / Risk Alerts
- **RESOLVED — login identifier:** login uses `email` + PIN. Email is human-friendly,
  unique, and supports multi-device login. This supersedes the earlier UUID-based login
  and requires the auth slice (US-6) to migrate `LoginRequest`/repository to email lookup.
- **DECISION — topic as TEXT+CHECK, not enum:** the topic taxonomy is expected to evolve;
  a CHECK constraint is cheaper to alter than a Postgres enum. `sentiment` and
  `physical_state` remain enums (stable sets).
- **DECISION — reminders stored inline on `ai_analyses`:** sufficient for v0.1.0. When
  US-4 (reminder notifications) lands, a dedicated `reminders` table will likely be split
  out; the inline columns make that migration straightforward.
- **NOTE — no RLS:** all access control lives in the FastAPI layer. The service-role key
  must never reach the mobile client.
```
