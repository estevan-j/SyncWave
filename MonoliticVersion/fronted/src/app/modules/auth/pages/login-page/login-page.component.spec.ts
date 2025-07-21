import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LoginPageComponent } from './login-page.component';
import { UserService } from '../../../../core/services/user.service';
import { ApiService } from '../../../../core/services/api.service';

describe('LoginPageComponent', () => {
  let component: LoginPageComponent;
  let fixture: ComponentFixture<LoginPageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LoginPageComponent],
      providers: [
        { provide: UserService, useValue: jasmine.createSpyObj('UserService', ['isAuthenticated', 'setCurrentUser']) },
        { provide: ApiService, useValue: jasmine.createSpyObj('ApiService', ['post']) }
      ]
    })
      .compileComponents();

    fixture = TestBed.createComponent(LoginPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
