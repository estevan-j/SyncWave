import { Injectable } from '@angular/core';
import { Observable, BehaviorSubject } from 'rxjs';
import io from 'socket.io-client';
import { environment } from '../../../environments/environment';

export interface ChatMessage {
    id?: number;
    user_id: number;
    username: string;
    message: string;
    timestamp: string;
    room: string;
}

@Injectable({
    providedIn: 'root'
})
export class WebSocketService {
    private socket: any;
    private messagesSubject = new BehaviorSubject<ChatMessage[]>([]);
    private connectedSubject = new BehaviorSubject<boolean>(false);

    public messages$ = this.messagesSubject.asObservable();
    public connected$ = this.connectedSubject.asObservable();

    constructor() {
        // Configuración simplificada y más estable
        this.socket = io(environment.production ? '' : 'http://localhost:5000', {
            transports: ['polling'],  // Solo usar polling inicialmente
            upgrade: false,           // No hacer upgrade a websocket
            forceNew: false,
            reconnection: true,
            reconnectionDelay: 2000,
            reconnectionAttempts: 3,
            timeout: 10000
        });

        this.setupSocketListeners();
    }

    private setupSocketListeners(): void {
        this.socket.on('connect', () => {
            console.log('✅ Conectado al servidor WebSocket - ID:', this.socket.id);
            this.connectedSubject.next(true);
        });

        this.socket.on('disconnect', (reason: string) => {
            console.log('❌ Desconectado del servidor WebSocket. Razón:', reason);
            this.connectedSubject.next(false);
        });

        this.socket.on('connect_error', (error: any) => {
            console.error('🔥 Error de conexión WebSocket:', error);
            console.error('🔍 Detalles del error:', {
                message: error.message,
                type: error.type,
                description: error.description
            });
            this.connectedSubject.next(false);
        });

        this.socket.on('reconnect', (attemptNumber: number) => {
            console.log(`🔄 Reconectado al WebSocket después de ${attemptNumber} intentos`);
            this.connectedSubject.next(true);
        });

        this.socket.on('reconnect_attempt', (attemptNumber: number) => {
            console.log(`🔄 Intentando reconectar... Intento ${attemptNumber}`);
        });

        this.socket.on('reconnect_error', (error: any) => {
            console.error('🔥 Error en reconexión:', error);
        });

        this.socket.on('reconnect_failed', () => {
            console.error('💀 Falló la reconexión después de todos los intentos');
        });

        // Status message from backend
        this.socket.on('status', (data: any) => {
            console.log('📡 Status:', data.msg);
        });

        // New message received
        this.socket.on('new_message', (message: ChatMessage) => {
            console.log('💬 Nuevo mensaje recibido:', message);
            const currentMessages = this.messagesSubject.value;
            this.messagesSubject.next([...currentMessages, message]);
        });

        // Recent messages when joining a room
        this.socket.on('recent_messages', (data: { messages: ChatMessage[] }) => {
            console.log('📜 Mensajes recientes:', data.messages);
            this.messagesSubject.next(data.messages);
        });

        // Message history response
        this.socket.on('message_history', (history: any) => {
            console.log('📚 Historial de mensajes:', history);
            if (history.messages) {
                this.messagesSubject.next(history.messages);
            }
        });

        // User events
        this.socket.on('user_joined', (data: any) => {
            console.log('👋 Usuario se unió:', data);
        });

        this.socket.on('user_left', (data: any) => {
            console.log('👋 Usuario salió:', data);
        });

        this.socket.on('user_disconnected', (data: any) => {
            console.log('🚪 Usuario desconectado:', data);
        });

        // Typing indicator
        this.socket.on('user_typing', (data: any) => {
            console.log('⌨️ Usuario escribiendo:', data);
        });

        // Error handling
        this.socket.on('error', (error: any) => {
            console.error('🔥 Error del WebSocket:', error);
            console.error('🔍 Tipo de error:', typeof error);
            console.error('🔍 Error stringificado:', JSON.stringify(error, null, 2));
        });
    }

    joinRoom(userId: number, username: string, room: string = 'general'): void {
        this.socket.emit('join_room', {
            user_id: userId,
            username: username,
            room: room
        });
    }

    leaveRoom(userId: number, room: string = 'general'): void {
        this.socket.emit('leave_room', {
            user_id: userId,
            room: room
        });
    }

    sendMessage(userId: number, username: string, message: string, room: string = 'general'): void {
        this.socket.emit('send_message', {
            user_id: userId,
            username: username,
            message: message,
            room: room
        });
    }

    getMessageHistory(room: string = 'general', page: number = 1, perPage: number = 20): void {
        this.socket.emit('get_message_history', {
            room: room,
            page: page,
            per_page: perPage
        });
    }

    sendTypingIndicator(userId: number, room: string = 'general', isTyping: boolean = false): void {
        this.socket.emit('typing', {
            user_id: userId,
            room: room,
            is_typing: isTyping
        });
    }

    disconnect(): void {
        if (this.socket) {
            this.socket.disconnect();
        }
    }

    clearMessages(): void {
        this.messagesSubject.next([]);
    }
}
