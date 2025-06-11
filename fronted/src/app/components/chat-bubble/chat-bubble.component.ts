import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Subscription } from 'rxjs';
import { WebSocketService, ChatMessage } from '../../core/services/websocket.service';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-chat-bubble',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chat-bubble.component.html',
  styleUrls: ['./chat-bubble.component.css']
})
export class ChatBubbleComponent implements OnInit, OnDestroy {
  chatVisible = false;
  message = '';
  messages: ChatMessage[] = [];
  currentUser: any;
  connected = false;
  room = 'general';

  private messagesSubscription?: Subscription;
  private connectedSubscription?: Subscription;
  private typingTimeout?: any;

  constructor(
    private webSocketService: WebSocketService,
    private authService: AuthService
  ) { }

  ngOnInit() {
    this.currentUser = this.authService.getCurrentUser();

    if (!this.currentUser) {
      // Si no hay usuario autenticado, crear un usuario temporal
      this.currentUser = {
        id: Math.floor(Math.random() * 10000),
        username: `Usuario_${Math.floor(Math.random() * 1000)}`,
        email: `temp${Math.floor(Math.random() * 1000)}@temp.com`
      };
    }

    // Suscribirse a los mensajes
    this.messagesSubscription = this.webSocketService.messages$.subscribe(
      messages => {
        this.messages = messages;
      }
    );

    // Suscribirse al estado de conexión
    this.connectedSubscription = this.webSocketService.connected$.subscribe(
      connected => {
        this.connected = connected;
        if (connected && this.chatVisible) {
          this.joinRoom();
        }
      }
    );
  }
  ngOnDestroy() {
    if (this.messagesSubscription) {
      this.messagesSubscription.unsubscribe();
    }
    if (this.connectedSubscription) {
      this.connectedSubscription.unsubscribe();
    }

    // Clear typing timeout
    if (this.typingTimeout) {
      clearTimeout(this.typingTimeout);
    }

    if (this.currentUser && this.connected) {
      this.webSocketService.leaveRoom(this.currentUser.id, this.room);
    }
  }

  toggleChat() {
    this.chatVisible = !this.chatVisible;

    if (this.chatVisible && this.connected && this.currentUser) {
      this.joinRoom();
    } else if (!this.chatVisible && this.currentUser) {
      this.webSocketService.leaveRoom(this.currentUser.id, this.room);
    }
  }

  private joinRoom() {
    if (this.currentUser && this.connected) {
      this.webSocketService.joinRoom(this.currentUser.id, this.currentUser.username, this.room);
    }
  }

  sendMessage() {
    if (!this.message.trim() || !this.currentUser || !this.connected) return;

    this.webSocketService.sendMessage(
      this.currentUser.id,
      this.currentUser.username,
      this.message.trim(),
      this.room
    );

    this.message = '';
  }
  formatTimestamp(timestamp: string): string {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  onTyping() {
    if (!this.currentUser || !this.connected) return;

    // Send typing indicator
    this.webSocketService.sendTypingIndicator(this.currentUser.id, this.room, true);

    // Clear previous timeout
    if (this.typingTimeout) {
      clearTimeout(this.typingTimeout);
    }

    // Set timeout to stop typing indicator after 2 seconds of inactivity
    this.typingTimeout = setTimeout(() => {
      this.onStopTyping();
    }, 2000);
  }

  onStopTyping() {
    if (!this.currentUser || !this.connected) return;

    // Send stop typing indicator
    this.webSocketService.sendTypingIndicator(this.currentUser.id, this.room, false);

    // Clear timeout
    if (this.typingTimeout) {
      clearTimeout(this.typingTimeout);
      this.typingTimeout = null;
    }
  }
}
