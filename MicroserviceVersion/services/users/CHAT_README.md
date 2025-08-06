# Chat Functionality - Users Microservice

## Overview

Se ha agregado funcionalidad completa de chat al microservicio de usuarios, migrando la lógica desde la versión monolítica. La funcionalidad incluye:

- **REST API endpoints** para operaciones de chat
- **WebSocket support** para chat en tiempo real
- **Persistencia de datos** usando Supabase
- **Validación de mensajes** y manejo de errores
- **Sistema de salas** para organizar conversaciones

## Estructura de Archivos

```
app/
├── controllers/
│   ├── auth_controller.py      # Autenticación existente
│   ├── chat_controller.py      # ✅ NUEVO: Endpoints REST para chat
│   └── websocket_controller.py # ✅ NUEVO: WebSocket handlers
├── services/
│   ├── auth_service.py         # Servicio de autenticación
│   └── chat_service.py         # ✅ NUEVO: Lógica de negocio del chat
├── schemas/
│   ├── auth_schema.py          # Esquemas de autenticación
│   └── chat_schema.py          # ✅ NUEVO: Esquemas de chat
└── exceptions/
    ├── user_exceptions.py      # Excepciones de usuarios
    └── chat_exceptions.py      # ✅ NUEVO: Excepciones de chat
```

## REST API Endpoints

### Chat Messages

#### POST `/api/chat/messages`
Enviar un nuevo mensaje de chat.

**Request Body:**
```json
{
  "message": "Hola mundo!",
  "room": "general",
  "user_id": "user123",
  "username": "John Doe"
}
```

**Response:**
```json
{
  "id": 1,
  "user_id": "user123",
  "username": "John Doe",
  "message": "Hola mundo!",
  "timestamp": "2024-01-15T10:30:00",
  "room": "general",
  "request_id": "req_123"
}
```

#### GET `/api/chat/messages`
Obtener mensajes recientes de una sala.

**Query Parameters:**
- `room` (opcional): Nombre de la sala (default: "general")
- `limit` (opcional): Número máximo de mensajes (default: 50, max: 100)

**Response:**
```json
{
  "messages": [...],
  "room": "general",
  "count": 25,
  "request_id": "req_123"
}
```

#### GET `/api/chat/messages/history`
Obtener historial paginado de mensajes.

**Query Parameters:**
- `room` (opcional): Nombre de la sala
- `page` (opcional): Número de página (default: 1)
- `per_page` (opcional): Mensajes por página (default: 20, max: 50)

#### DELETE `/api/chat/messages/{message_id}`
Eliminar un mensaje (solo el autor puede eliminarlo).

**Request Body:**
```json
{
  "user_id": "user123"
}
```

### Chat Rooms

#### GET `/api/chat/rooms`
Obtener lista de salas activas.

**Response:**
```json
{
  "rooms": ["general", "music", "tech"],
  "count": 3,
  "request_id": "req_123"
}
```

#### GET `/api/chat/rooms/{room_name}/statistics`
Obtener estadísticas de una sala específica.

**Response:**
```json
{
  "room": "general",
  "message_count": 150,
  "last_message": {
    "id": 150,
    "user_id": "user123",
    "username": "John Doe",
    "message": "Último mensaje",
    "timestamp": "2024-01-15T10:30:00",
    "room": "general"
  },
  "request_id": "req_123"
}
```

### Debug

#### GET `/api/chat/debug`
Endpoint de debug para verificar el estado del servicio de chat.

## WebSocket Events

### Conexión
```javascript
// Conectar al WebSocket
const socket = io('http://localhost:5000');

// Eventos de conexión
socket.on('connect', () => {
  console.log('Conectado al chat');
});

socket.on('disconnect', () => {
  console.log('Desconectado del chat');
});
```

### Unirse/Salir de Salas
```javascript
// Unirse a una sala
socket.emit('join_room', {
  user_id: 'user123',
  room: 'general',
  username: 'John Doe'
});

// Salir de una sala
socket.emit('leave_room', {
  user_id: 'user123',
  room: 'general',
  username: 'John Doe'
});

// Eventos de sala
socket.on('user_joined', (data) => {
  console.log(`${data.username} se unió a la sala`);
});

socket.on('user_left', (data) => {
  console.log(`${data.username} salió de la sala`);
});
```

### Enviar/Recibir Mensajes
```javascript
// Enviar mensaje
socket.emit('send_message', {
  message: 'Hola mundo!',
  room: 'general',
  user_id: 'user123',
  username: 'John Doe'
});

// Recibir mensajes
socket.on('new_message', (message) => {
  console.log(`${message.username}: ${message.message}`);
});

socket.on('recent_messages', (data) => {
  console.log('Mensajes recientes:', data.messages);
});
```

### Indicadores de Escritura
```javascript
// Enviar indicador de escritura
socket.emit('typing', {
  user_id: 'user123',
  room: 'general',
  username: 'John Doe',
  is_typing: true
});

// Recibir indicadores de escritura
socket.on('user_typing', (data) => {
  console.log(`${data.username} está escribiendo...`);
});
```

### Historial y Usuarios
```javascript
// Obtener historial
socket.emit('get_message_history', {
  room: 'general',
  page: 1,
  per_page: 20
});

socket.on('message_history', (history) => {
  console.log('Historial:', history);
});

// Obtener usuarios conectados
socket.emit('get_connected_users', {
  room: 'general'
});

socket.on('connected_users', (data) => {
  console.log('Usuarios conectados:', data.users);
});
```

## Base de Datos

### Tabla `chat_messages`
```sql
CREATE TABLE chat_messages (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR NOT NULL,
  username VARCHAR NOT NULL,
  message TEXT NOT NULL,
  room VARCHAR(50) DEFAULT 'general',
  timestamp TIMESTAMP DEFAULT NOW()
);
```

## Configuración

### Variables de Entorno
```bash
# Supabase (ya configurado)
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Logging
LOG_LEVEL=INFO
SERVICE_NAME=users-auth
```

### Dependencias Agregadas
```txt
flask-socketio==5.3.6
python-socketio==5.9.0
```

## Migración desde Monolítico

### Cambios Principales:

1. **Base de Datos**: Cambio de SQLAlchemy a Supabase
2. **Validación**: Uso de Pydantic para validación de esquemas
3. **Logging**: Integración con sistema de logging compartido
4. **WebSocket**: Configuración optimizada para microservicios
5. **Manejo de Errores**: Excepciones personalizadas para chat

### Funcionalidades Migradas:

- ✅ Envío y recepción de mensajes
- ✅ Sistema de salas
- ✅ Historial paginado
- ✅ Eliminación de mensajes (solo autor)
- ✅ Indicadores de escritura
- ✅ WebSocket en tiempo real
- ✅ Validación de mensajes
- ✅ Manejo de errores

## Testing

### Endpoints REST
```bash
# Enviar mensaje
curl -X POST http://localhost:5000/api/chat/messages \
  -H "Content-Type: application/json" \
  -d '{"message":"Test message","user_id":"test123","room":"general"}'

# Obtener mensajes
curl http://localhost:5000/api/chat/messages?room=general

# Obtener salas
curl http://localhost:5000/api/chat/rooms
```

### WebSocket Testing
```javascript
// Usar herramientas como Postman o un cliente WebSocket
// para probar los eventos de WebSocket
```

## Notas de Implementación

1. **Seguridad**: Los mensajes se validan antes de guardar
2. **Escalabilidad**: Diseñado para funcionar en múltiples instancias
3. **Logging**: Logs detallados para debugging y monitoreo
4. **Error Handling**: Manejo robusto de errores con respuestas consistentes
5. **Performance**: Paginación y límites para evitar sobrecarga

## Próximos Pasos

1. Implementar autenticación JWT para WebSocket
2. Agregar notificaciones push
3. Implementar archivos adjuntos en mensajes
4. Agregar moderación de contenido
5. Implementar búsqueda de mensajes 