-- Migración para agregar campo username a tabla users
-- Ejecutar este script en PostgreSQL

-- Agregar columna username si no existe
ALTER TABLE users ADD COLUMN IF NOT EXISTS username VARCHAR(50) DEFAULT NULL;

-- Verificar que la columna se agregó
\d users

-- Opcional: Actualizar usuarios existentes con un username temporal
UPDATE users 
SET username = CONCAT('User_', id) 
WHERE username IS NULL OR username = '';

-- Verificar los cambios
SELECT id, email, username, created_at FROM users LIMIT 5;

-- Mensaje de confirmación
SELECT 'Migración completada: campo username agregado exitosamente' AS result;
