-- Crear tabla de refresh_tokens
CREATE TABLE IF NOT EXISTS public.refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    token TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Índices para búsqueda rápida y limpieza
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token ON public.refresh_tokens(token);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON public.refresh_tokens(user_id);

-- Configurar RLS (Row Level Security)
ALTER TABLE public.refresh_tokens ENABLE ROW LEVEL SECURITY;

-- Políticas de RLS
-- Nota: En la arquitectura actual, el backend (FastAPI) interactúa usando la service_role key, 
-- por lo que sobrepasa estas políticas. Se agregan por seguridad si alguna vez se expone al cliente.
CREATE POLICY "Users can only view their own refresh tokens"
    ON public.refresh_tokens FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can only delete their own refresh tokens"
    ON public.refresh_tokens FOR DELETE
    USING (auth.uid() = user_id);
