import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ChatBubbleComponent } from './chat-bubble.component';
import { WebSocketService } from '../../core/services/websocket.service';
import { AuthService } from '../../core/services/auth.service';
import { of } from 'rxjs';

describe('ChatBubbleComponent', () => {
  let component: ChatBubbleComponent;
  let fixture: ComponentFixture<ChatBubbleComponent>;
  let mockWebSocketService: jasmine.SpyObj<WebSocketService>;
  let mockAuthService: jasmine.SpyObj<AuthService>;

  beforeEach(async () => {
    const webSocketSpy = jasmine.createSpyObj('WebSocketService', ['joinRoom', 'leaveRoom', 'sendMessage'], {
      messages$: of([]),
      connected$: of(true)
    });

    const authSpy = jasmine.createSpyObj('AuthService', ['getCurrentUser'], {
      getCurrentUser: () => ({ id: 1, username: 'Test User', email: 'test@test.com' })
    });

    await TestBed.configureTestingModule({
      imports: [ChatBubbleComponent],
      providers: [
        { provide: WebSocketService, useValue: webSocketSpy },
        { provide: AuthService, useValue: authSpy }
      ]
    })
      .compileComponents();

    fixture = TestBed.createComponent(ChatBubbleComponent);
    component = fixture.componentInstance;
    mockWebSocketService = TestBed.inject(WebSocketService) as jasmine.SpyObj<WebSocketService>;
    mockAuthService = TestBed.inject(AuthService) as jasmine.SpyObj<AuthService>;

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should toggle chat visibility', () => {
    expect(component.chatVisible).toBeFalse();
    component.toggleChat();
    expect(component.chatVisible).toBeTrue();
  });

  it('should send message when connected and message is not empty', () => {
    component.connected = true;
    component.message = 'Test message';
    component.currentUser = { id: 1, username: 'Test User' };

    component.sendMessage();

    expect(mockWebSocketService.sendMessage).toHaveBeenCalledWith(1, 'Test User', 'Test message', 'general');
    expect(component.message).toBe('');
  });

  it('should not send message when not connected', () => {
    component.connected = false;
    component.message = 'Test message';

    component.sendMessage();

    expect(mockWebSocketService.sendMessage).not.toHaveBeenCalled();
  });
});
