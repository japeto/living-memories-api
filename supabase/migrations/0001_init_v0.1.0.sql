-- ============================================================================
-- 0001_init_v0.1.0.sql — Mi Recuerdo Vivo — initial schema (v0.1.0)
--
-- Covers: auth (US-6), audio_management (US-10, US-13), ai_analysis (US-11, US-12).
-- audio_recordings is the central entity; transcriptions and ai_analyses are
-- 1-to-1 children. Access control lives in the FastAPI layer (service-role key,
-- no RLS in v0.1.0).
-- ============================================================================

-- Extensions ------------------------------------------------------------------
-- Case-insensitive text for emails (so 'A@x.com' == 'a@x.com' for uniqueness).
create extension if not exists citext;

-- Enum types (stable, small value sets) ---------------------------------------
create type recording_status as enum ('pending', 'transcribed', 'analyzed', 'failed');
create type sentiment_label  as enum ('positive', 'neutral', 'negative');
create type physical_state   as enum ('good', 'regular', 'poor');

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
