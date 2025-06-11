#!/bin/bash
set -e

# Script de inicialización para la base de datos PostgreSQL
# Este script se ejecuta automáticamente cuando se crea el contenedor por primera vez

# Crear extensiones necesarias
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Crear extensión para UUID
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    
    -- Crear extensión para funciones de texto
    CREATE EXTENSION IF NOT EXISTS "unaccent";
    
    -- Crear extensión para búsqueda de texto completo
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";
    
    -- Configurar zona horaria
    SET timezone = 'America/Lima';
    
    -- Crear función para actualizar timestamps automáticamente
    CREATE OR REPLACE FUNCTION update_modified_column()
    RETURNS TRIGGER AS \$\$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    \$\$ language 'plpgsql';
EOSQL

echo "✅ Extensiones y funciones creadas correctamente"

# Crear tablas iniciales según el nuevo diagrama (FAVORITE_SONGS)
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL    -- Tabla de usuarios (ACTUALIZADA con password y username)
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(120) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,        -- ✨ NUEVO CAMPO PASSWORD
        username VARCHAR(50),                  -- ✨ NUEVO CAMPO USERNAME
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Tabla de canciones (actualizada con campos del JSON)
    CREATE TABLE IF NOT EXISTS songs (
        id SERIAL PRIMARY KEY,
        title VARCHAR(200) NOT NULL,           -- "name" del JSON
        artist VARCHAR(100) NOT NULL,          -- "artist.name" simplificado
        album VARCHAR(100),                    -- "album" del JSON
        duration INTEGER,                      -- "duration.end" del JSON (en segundos)
        file_path VARCHAR(500),                -- "url" del JSON
        cover_url VARCHAR(500),                -- "cover" del JSON ✨
        artist_name VARCHAR(100),              -- "artist.name" completo ✨
        artist_nickname VARCHAR(100),          -- "artist.nickname" del JSON ✨
        nationality VARCHAR(10),               -- "artist.nationality" del JSON ✨
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Tabla de canciones favoritas (reemplaza playlists)
    CREATE TABLE IF NOT EXISTS favorite_songs (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        song_id INTEGER NOT NULL REFERENCES songs(id) ON DELETE CASCADE,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, song_id) -- Un usuario no puede tener la misma canción como favorita dos veces
    );

    -- Tabla de mensajes de chat
    CREATE TABLE IF NOT EXISTS chat_messages (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        message TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        room VARCHAR(50) DEFAULT 'general'
    );

    -- Crear triggers para actualizar timestamps automáticamente
    CREATE TRIGGER update_users_modtime 
        BEFORE UPDATE ON users 
        FOR EACH ROW EXECUTE FUNCTION update_modified_column();
        
    CREATE TRIGGER update_songs_modtime 
        BEFORE UPDATE ON songs 
        FOR EACH ROW EXECUTE FUNCTION update_modified_column();
EOSQL

echo "✅ Tablas creadas correctamente"

# Crear índices para optimizar consultas
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Índices para búsquedas optimizadas
    CREATE INDEX IF NOT EXISTS idx_songs_artist ON songs USING gin(artist gin_trgm_ops);
    CREATE INDEX IF NOT EXISTS idx_songs_artist_name ON songs(artist_name);
    CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
    CREATE INDEX IF NOT EXISTS idx_favorite_songs_user_id ON favorite_songs(user_id);
    CREATE INDEX IF NOT EXISTS idx_favorite_songs_song_id ON favorite_songs(song_id);
EOSQL

