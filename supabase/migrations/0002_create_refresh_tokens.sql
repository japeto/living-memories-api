-- Create refresh_tokens table
CREATE TABLE IF NOT EXISTS public.refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    token TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes for fast lookup and cleanup
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token ON public.refresh_tokens(token);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON public.refresh_tokens(user_id);

-- Configure Row Level Security (RLS)
ALTER TABLE public.refresh_tokens ENABLE ROW LEVEL SECURITY;

-- RLS Policies
-- Note: In the current architecture, the backend (FastAPI) interacts using the service_role key,
-- so it bypasses these policies. They are added for security if it is ever exposed to the client.
CREATE POLICY "Users can only view their own refresh tokens"
    ON public.refresh_tokens FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can only delete their own refresh tokens"
    ON public.refresh_tokens FOR DELETE
    USING (auth.uid() = user_id);
