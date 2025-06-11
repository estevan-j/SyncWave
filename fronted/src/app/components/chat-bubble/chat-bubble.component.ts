import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-chat-bubble',
  standalone: true, // 👈 Esto es muy importante
  imports: [CommonModule, FormsModule],
  templateUrl: './chat-bubble.component.html',
  styleUrls: ['./chat-bubble.component.css']
})
export class ChatBubbleComponent {
  chatVisible = false;
  message = '';
  messages: string[] = [];

  toggleChat() {
    this.chatVisible = !this.chatVisible;
  }

  sendMessage() {
    if (!this.message.trim()) return;
    this.messages.push(this.message);
    this.message = '';
  }
}
