# Music App Backend

Una aplicación Flask monolítica con API REST, WebSockets para chat en tiempo real y base de datos SQLAlchemy.

## 🏗️ Arquitectura del Proyecto

```
backend/
├── app/
│   ├── __init__.py
│   ├── config.py                 # Configuración de la app
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py              # Modelo User (legacy)
│   │   ├── song.py              # Modelo Song (legacy)
│   │   ├── playlist.py          # Modelo Playlist (legacy)
│   │   └── database.py          # Modelos SQLAlchemy (User, Song, Playlist, ChatMessage)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── users.py             # Endpoints REST para usuarios
│   │   ├── music.py             # Endpoints REST para canciones
│   │   ├── playlists.py         # Endpoints REST para playlists
│   │   └── chat.py              # Endpoints REST y handlers WebSocket para chat
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user_service.py      # Lógica de negocio para usuarios
│   │   ├── music_service.py     # Lógica de negocio para música
│   │   ├── playlist_service.py  # Lógica de negocio para playlists
│   │   └── chat_service.py      # Lógica de negocio para chat
│   └── utils/
│       ├── __init__.py
│       ├── validators.py        # Validaciones de datos
│       └── responses.py         # Helpers para respuestas API
├── uploads/                     # Archivos de música subidos
├── app.py                       # Punto de entrada principal
├── requirements.txt             # Dependencias Python
├── .env.example                 # Variables de entorno ejemplo
└── .gitignore                   # Archivos ignorados por Git
```

## 📋 Responsabilidades de Cada Capa

### 🔧 **config.py** - Configuración Central
- Gestiona variables de entorno
- Configuraciones por ambiente (desarrollo/producción)
- Configuración de base de datos SQLAlchemy
- Configuración de WebSocket/SocketIO
- Configuración de CORS

### 📊 **models/** - Capa de Datos
#### `database.py` - Modelos SQLAlchemy (Principal)
- **User**: Usuarios de la aplicación
- **Song**: Canciones con metadatos
- **Playlist**: Listas de reproducción con relación many-to-many a canciones
- **ChatMessage**: Mensajes de chat con timestamps y salas

#### Archivos legacy (`user.py`, `song.py`, `playlist.py`)
- Modelos simples sin base de datos (para referencia)

### 🛣️ **routes/** - Capa de Presentación
#### `users.py` - API REST para Usuarios
- `GET /api/users/` - Listar usuarios
- `POST /api/users/` - Crear usuario
- `GET /api/users/{id}` - Obtener usuario específico
- `PUT /api/users/{id}` - Actualizar usuario
- `DELETE /api/users/{id}` - Eliminar usuario

#### `music.py` - API REST para Música
- `GET /api/music/songs` - Listar canciones
- `POST /api/music/songs` - Crear canción
- `GET /api/music/songs/{id}` - Obtener canción específica
- `PUT /api/music/songs/{id}` - Actualizar canción
- `DELETE /api/music/songs/{id}` - Eliminar canción
- `GET /api/music/songs/search?q=query` - Buscar canciones

#### `playlists.py` - API REST para Playlists
- `GET /api/playlists/` - Listar playlists
- `POST /api/playlists/` - Crear playlist
- `GET /api/playlists/{id}` - Obtener playlist específica
- `PUT /api/playlists/{id}` - Actualizar playlist
- `DELETE /api/playlists/{id}` - Eliminar playlist
- `POST /api/playlists/{id}/songs` - Agregar canción a playlist
- `DELETE /api/playlists/{id}/songs/{song_id}` - Remover canción de playlist
- `GET /api/playlists/user/{user_id}` - Playlists de un usuario

#### `chat.py` - Chat en Tiempo Real
**Endpoints REST:**
- `GET /api/chat/rooms` - Obtener salas activas
- `GET /api/chat/rooms/{room}/messages` - Historial de mensajes
- `DELETE /api/chat/messages/{id}` - Eliminar mensaje

**Eventos WebSocket:**
- `connect` - Cliente se conecta
- `disconnect` - Cliente se desconecta
- `join_room` - Unirse a sala de chat
- `leave_room` - Salir de sala de chat
- `send_message` - Enviar mensaje
- `typing` - Indicador de escritura
- `get_message_history` - Obtener historial

### ⚙️ **services/** - Lógica de Negocio
#### `user_service.py`
- Validación de datos de usuario
- Búsqueda de usuarios
- Lógica de negocio para gestión de usuarios

#### `music_service.py`
- Validación de archivos de música
- Procesamiento de uploads
- Validación de metadatos de canciones
- Funciones de búsqueda y filtrado

#### `playlist_service.py`
- Validación de datos de playlist
- Cálculo de duración total
- Duplicación de playlists
- Obtención de detalles de canciones en playlist

#### `chat_service.py`
- Persistencia de mensajes en base de datos
- Obtención de historial paginado
- Gestión de salas de chat
- Validación de mensajes
- Eliminación de mensajes

### 🔧 **utils/** - Utilidades Compartidas
#### `validators.py`
- Validación de emails
- Validación de nombres de usuario
- Validación de títulos de canciones
- Validación de duraciones
- Validación de extensiones de archivo

#### `responses.py`
- Respuestas API estandarizadas
- Manejo de errores consistente
- Respuestas paginadas
- Códigos de estado HTTP apropiados

## 🚀 Características Principales

### 🎵 **Gestión de Música**
- CRUD completo para canciones
- Metadatos (título, artista, álbum, duración)
- Búsqueda de canciones
- Upload de archivos de música

### 📝 **Sistema de Playlists**
- Creación y gestión de playlists
- Relación many-to-many con canciones
- Playlists por usuario
- Cálculo automático de duración

### 👥 **Gestión de Usuarios**
- Registro y gestión de usuarios
- Validación de emails
- Perfiles de usuario

### 💬 **Chat en Tiempo Real**
- WebSocket con Flask-SocketIO
- Múltiples salas de chat
- Historial persistente en base de datos
- Indicadores de escritura
- Usuarios conectados en tiempo real

### 🗄️ **Base de Datos SQLAlchemy**
- SQLite para desarrollo
- PostgreSQL ready para producción
- Migraciones automáticas
- Relaciones entre modelos

## 🛠️ Instalación y Configuración

### Dependencias
```bash
pip install -r requirements.txt
```

### Variables de Entorno
Copia `.env.example` a `.env` y configura:
```bash
SECRET_KEY=your-secret-key-here
FLASK_DEBUG=True
PORT=5000
UPLOAD_FOLDER=uploads
DATABASE_URL=sqlite:///musicapp.db
```

### Ejecutar la Aplicación
```bash
python app.py
```

## 🌐 Integración con Frontend

### REST API
- **Base URL**: `http://localhost:5000/api/`
- **CORS**: Configurado para React, Vue, Angular
- **Formato**: JSON requests/responses
- **Códigos HTTP**: Estándares REST

### WebSocket (Chat)
- **URL**: `ws://localhost:5000/`
- **Protocolo**: Socket.IO
- **Salas**: Soporte para múltiples salas
- **Eventos**: En tiempo real bidireccional

### Ejemplo de Conexión WebSocket (JavaScript)
```javascript
import io from 'socket.io-client';

const socket = io('http://localhost:5000');

// Unirse a sala
socket.emit('join_room', {
  user_id: 1,
  room: 'general',
  username: 'usuario'
});

// Enviar mensaje
socket.emit('send_message', {
  user_id: 1,
  message: 'Hola mundo!',
  room: 'general'
});

// Recibir mensajes
socket.on('new_message', (data) => {
  console.log('Nuevo mensaje:', data);
});
```

## 🔄 Flujo de Datos

```
Frontend (React/Vue) 
    ↓ HTTP REST API
routes/ (users, music, playlists)
    ↓ 
services/ (business logic)
    ↓ 
models/database.py (SQLAlchemy)
    ↓ 
SQLite/PostgreSQL Database

Frontend (WebSocket Client)
    ↓ Socket.IO events
routes/chat.py (WebSocket handlers)
    ↓ 
services/chat_service.py
    ↓ 
models/database.py (ChatMessage)
    ↓ 
Database + Broadcast to clients
```

Esta arquitectura permite escalabilidad, mantenibilidad y separación clara de responsabilidades, ideal para una aplicación de música con chat en tiempo real.
