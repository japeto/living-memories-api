-- 0003_create_memories.sql
-- Create memories table

CREATE TABLE IF NOT EXISTS public.memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    topic TEXT,
    mood TEXT,
    reminder_text TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
