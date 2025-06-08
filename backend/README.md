# Music App Backend

Una aplicación Flask con API REST, WebSockets para chat en tiempo real y base de datos PostgreSQL.

## 🏗️ Arquitectura del Proyecto

```
backend/
├── app/
│   ├── __init__.py
│   ├── config.py                 # Configuración de la app
│   ├── models/
│   │   ├── __init__.py
│   │   └── database.py          # Modelos SQLAlchemy (User, Song, FavoriteSong, ChatMessage)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── users.py             # Endpoints REST para usuarios
│   │   ├── music.py             # Endpoints REST para canciones
│   │   ├── favorites.py         # Endpoints REST para canciones favoritas
│   │   └── chat.py              # Endpoints REST y handlers WebSocket para chat
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user_service.py      # Lógica de negocio para usuarios
│   │   ├── music_service.py     # Lógica de negocio para música
│   │   └── chat_service.py      # Lógica de negocio para chat
│   └── utils/
│       ├── __init__.py
│       ├── validators.py        # Validaciones de datos
│       └── responses.py         # Helpers para respuestas API
├── uploads/                     # Archivos de música subidos
├── app.py                       # Punto de entrada principal
├── init_db.py                   # Script de inicialización de base de datos
├── requirements.txt             # Dependencias Python
├── .env.example                 # Variables de entorno ejemplo
└── .gitignore                   # Archivos ignorados por Git
```

## 📋 Responsabilidades de Cada Capa

### 🔧 **config.py** - Configuración Central
- Gestiona variables de entorno
- Configuraciones por ambiente (desarrollo/producción)
- Configuración de base de datos PostgreSQL
- Configuración de WebSocket/SocketIO
- Configuración de CORS

### 📊 **models/database.py** - Modelos de Base de Datos

#### Entidades Principales:

##### 👤 **User**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

##### 🎵 **Song**
```sql
CREATE TABLE songs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,           -- Título de la canción
    artist VARCHAR(100) NOT NULL,          -- Artista simplificado
    album VARCHAR(100),                    -- Álbum
    duration INTEGER,                      -- Duración en segundos
    file_path VARCHAR(500),                -- URL del archivo
    cover_url VARCHAR(500),                -- URL de la portada
    artist_name VARCHAR(100),              -- Nombre completo del artista
    artist_nickname VARCHAR(100),          -- Apodo del artista
    nationality VARCHAR(10),               -- Nacionalidad del artista
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

##### ⭐ **FavoriteSong** (Reemplaza Playlists)
```sql
CREATE TABLE favorite_songs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    song_id INTEGER NOT NULL REFERENCES songs(id) ON DELETE CASCADE,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, song_id)
);
```

##### 💬 **ChatMessage**
```sql
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    room VARCHAR(50) DEFAULT 'general'
);
```

### 🛣️ **routes/** - Endpoints API

#### 👤 **users.py** - Gestión de Usuarios
```
GET    /api/users                      # Listar todos los usuarios
POST   /api/users                      # Crear nuevo usuario
GET    /api/users/<id>                 # Obtener usuario específico
PUT    /api/users/<id>                 # Actualizar usuario
DELETE /api/users/<id>                 # Eliminar usuario
POST   /api/users/login                # Login de usuario
POST   /api/users/check-email          # Verificar si email existe
GET    /api/users/search?q=<query>     # Buscar usuarios
```

#### 🎵 **music.py** - Gestión de Música
```
GET    /api/music/songs                        # Listar todas las canciones
POST   /api/music/songs                        # Crear nueva canción
GET    /api/music/songs/<id>                   # Obtener canción específica
PUT    /api/music/songs/<id>                   # Actualizar canción
DELETE /api/music/songs/<id>                   # Eliminar canción
GET    /api/music/songs/search?q=<query>       # Buscar canciones
GET    /api/music/songs/by-artist/<artist>     # Canciones por artista
GET    /api/music/songs/by-nationality/<nat>   # Canciones por nacionalidad
POST   /api/music/upload                       # Subir archivo de música
```

#### ⭐ **favorites.py** - Gestión de Favoritos
```
GET    /api/favorites/user/<user_id>                      # Favoritos del usuario
POST   /api/favorites/user/<user_id>/song/<song_id>       # Agregar a favoritos
DELETE /api/favorites/user/<user_id>/song/<song_id>       # Quitar de favoritos
GET    /api/favorites/user/<user_id>/song/<song_id>/check # Verificar si es favorito
GET    /api/favorites/song/<song_id>/users                # Usuarios que favoritearon
```

#### 💬 **chat.py** - Chat en Tiempo Real
```
# REST Endpoints
GET    /api/chat/messages              # Obtener mensajes recientes
POST   /api/chat/messages              # Enviar mensaje
GET    /api/chat/rooms                 # Listar salas disponibles

# WebSocket Events
connect                                # Conectar al chat
disconnect                             # Desconectar del chat
join_room                              # Unirse a sala
leave_room                             # Salir de sala
send_message                           # Enviar mensaje
get_message_history                    # Obtener historial
typing                                 # Indicador de escritura
```

## 🚀 Instalación y Configuración

### Prerrequisitos
- Python 3.8+
- PostgreSQL
- Docker (opcional)

### 1. Configuración del Entorno

```bash
# Clonar el repositorio
git clone <repository-url>
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuración de Base de Datos

#### Usando Docker (Recomendado)
```bash
# Levantar PostgreSQL con Docker
docker run --name musicapp-postgres \
  -e POSTGRES_DB=musicapp \
  -e POSTGRES_USER=musicapp_user \
  -e POSTGRES_PASSWORD=musicapp_password \
  -p 5432:5432 \
  -d postgres:13
```

#### Manual
```sql
-- Crear base de datos
CREATE DATABASE musicapp;
CREATE USER musicapp_user WITH PASSWORD 'musicapp_password';
GRANT ALL PRIVILEGES ON DATABASE musicapp TO musicapp_user;
```

### 3. Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar variables necesarias
nano .env
```

Configuración `.env`:
```bash
# Configuración Flask
SECRET_KEY=your-super-secret-key-change-in-production
FLASK_DEBUG=True
FLASK_ENV=development
PORT=5000
HOST=0.0.0.0

# Base de datos PostgreSQL
DATABASE_URL=postgresql://musicapp_user:musicapp_password@localhost:5432/musicapp
DB_HOST=localhost
DB_PORT=5432
DB_NAME=musicapp
DB_USER=musicapp_user
DB_PASSWORD=musicapp_password

# Uploads
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216  # 16MB
```

### 4. Inicializar Base de Datos

```bash
# Ejecutar script de inicialización
python init_db.py
```

Este script:
- Crea todas las tablas necesarias
- Inserta datos de ejemplo
- Crea usuarios de prueba
- Añade canciones de muestra
- Configura favoritos iniciales

### 5. Ejecutar la Aplicación

```bash
# Modo desarrollo
python app.py

# O usando Flask directamente
flask run

# Modo producción con Gunicorn
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 app:app
```

## 📡 Uso de la API

### Autenticación

```bash
# Crear usuario
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Login
curl -X POST http://localhost:5000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### Gestión de Música

```bash
# Listar canciones
curl http://localhost:5000/api/music/songs

# Buscar canciones
curl "http://localhost:5000/api/music/songs/search?q=queen"

# Obtener canciones por nacionalidad
curl http://localhost:5000/api/music/songs/by-nationality/US
```

### Gestión de Favoritos

```bash
# Ver favoritos de usuario
curl http://localhost:5000/api/favorites/user/1

# Agregar a favoritos
curl -X POST http://localhost:5000/api/favorites/user/1/song/1

# Verificar si es favorito
curl http://localhost:5000/api/favorites/user/1/song/1/check
```

## 🔧 Desarrollo

### Estructura de Respuestas API

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    // Datos de respuesta
  }
}
```

### Manejo de Errores

```json
{
  "success": false,
  "message": "Error description",
  "error_code": "ERROR_TYPE"
}
```

### WebSocket Events

```javascript
// Cliente JavaScript
const socket = io('http://localhost:5000');

// Conectar y unirse a sala
socket.emit('join_room', {room: 'general'});

// Enviar mensaje
socket.emit('send_message', {
  room: 'general',
  message: 'Hello world!'
});

// Escuchar mensajes
socket.on('receive_message', (data) => {
  console.log('New message:', data);
});
```

## 🧪 Testing

```bash
# Verificar salud de la API
curl http://localhost:5000/api/health

# Verificar endpoints
curl http://localhost:5000/

# Testing de WebSockets (usar cliente WebSocket)
```

## 📦 Deployment

### Con Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:5000", "app:app"]
```

### Con Docker Compose

```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://musicapp_user:musicapp_password@db:5432/musicapp
    depends_on:
      - db
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=musicapp
      - POSTGRES_USER=musicapp_user
      - POSTGRES_PASSWORD=musicapp_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## 🔍 Logging y Monitoreo

La aplicación incluye:
- Logging estructurado
- Manejo centralizado de errores
- Health checks
- Métricas de WebSocket

## 📄 Licencia

Este proyecto está bajo la licencia MIT.
