-- Script para crear la tabla chat_messages en Supabase
-- Ejecutar en el SQL Editor de Supabase

-- Crear tabla chat_messages
CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    username VARCHAR NOT NULL,
    message TEXT NOT NULL,
    room VARCHAR(50) DEFAULT 'general',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Crear índices para mejorar performance
CREATE INDEX IF NOT EXISTS idx_chat_messages_room ON chat_messages(room);
CREATE INDEX IF NOT EXISTS idx_chat_messages_timestamp ON chat_messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_chat_messages_user_id ON chat_messages(user_id);

-- Crear política RLS (Row Level Security) para permitir acceso completo
-- Nota: En producción, deberías configurar políticas más restrictivas
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;

-- Política para permitir todas las operaciones (para desarrollo)
CREATE POLICY "Allow all operations" ON chat_messages
    FOR ALL USING (true);

-- Comentarios para documentación
COMMENT ON TABLE chat_messages IS 'Tabla para almacenar mensajes de chat';
COMMENT ON COLUMN chat_messages.id IS 'ID único del mensaje';
COMMENT ON COLUMN chat_messages.user_id IS 'ID del usuario que envió el mensaje';
COMMENT ON COLUMN chat_messages.username IS 'Nombre de usuario del remitente';
COMMENT ON COLUMN chat_messages.message IS 'Contenido del mensaje';
COMMENT ON COLUMN chat_messages.room IS 'Sala donde se envió el mensaje';
COMMENT ON COLUMN chat_messages.timestamp IS 'Fecha y hora del mensaje';

-- Verificar que la tabla se creó correctamente
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'chat_messages'
ORDER BY ordinal_position; 