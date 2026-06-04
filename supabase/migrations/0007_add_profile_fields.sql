-- Migration: 0007_add_profile_fields.sql
-- Add full_name and avatar_url to users table

ALTER TABLE public.users
ADD COLUMN IF NOT EXISTS full_name text,
ADD COLUMN IF NOT EXISTS avatar_url text;
