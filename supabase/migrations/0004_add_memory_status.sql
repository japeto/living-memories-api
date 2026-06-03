ALTER TABLE memories
ADD COLUMN status text NOT NULL DEFAULT 'processing';

ALTER TABLE memories
ADD COLUMN title text;
