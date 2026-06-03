-- Cambiar el valor por defecto a 'completed' para que las memorias futuras (si no se especifica) 
-- y las antiguas no queden atascadas en 'processing'
ALTER TABLE memories
ALTER COLUMN status SET DEFAULT 'completed';

-- Actualizar todas las memorias antiguas que se quedaron atascadas en 'processing'
-- (Si acaban de ser creadas, el update las marcará como completadas, pero el fix real 
-- es para las que ya existían antes de la IA)
UPDATE memories 
SET status = 'completed' 
WHERE status = 'processing';
