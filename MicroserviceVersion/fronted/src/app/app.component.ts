import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { ChatBubbleComponent } from './components/chat-bubble/chat-bubble.component'; // 👈 Ajusta la ruta si cambia

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, ChatBubbleComponent], // 👈 Aquí lo estás declarando
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {}
