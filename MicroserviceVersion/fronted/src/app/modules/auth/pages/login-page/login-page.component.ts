import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { UserService } from '../../../../core/services/user.service';
import { AuthService } from '../../../../core/services/auth.service';

@Component({
  selector: 'app-login-page',
  templateUrl: './login-page.component.html',
  styleUrls: ['./login-page.component.css'],
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule]
})
export class LoginPageComponent implements OnInit {
  loginForm: FormGroup;
  loading = false;
  showPopup = false;
  popupTitle = '';
  popupMessage = '';
  popupType = 'success';

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private userService: UserService,
    private authService: AuthService
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }

  ngOnInit(): void {
    if (this.authService.isAuthenticated()) {
      this.router.navigate(['/home']);
    }
  }

  onLogin(): void {
    if (this.loginForm.invalid) {
      return;
    }

    this.loading = true;
    const { email, password } = this.loginForm.value;

    this.authService.login(email, password)
      .subscribe({
        next: (response: any) => {
          this.showSuccessPopup('Inicio de sesión exitoso', 'Bienvenido a Polimusic');
          setTimeout(() => {
            this.router.navigate(['/home']);
          }, 1500);
        },
        error: (error) => {
          if (error.status === 401) {
            this.showErrorPopup('Error de autenticación', 'Correo electrónico o contraseña incorrectos');
          } else {
            this.showErrorPopup('Error', 'Ocurrió un error al intentar iniciar sesión');
          }
          this.loading = false;
        },
        complete: () => {
          this.loading = false;
        }
      });
  }

  goToRegister(): void {
    this.router.navigate(['/auth/register']);
  }

  goToForgotPassword(): void {
    this.router.navigate(['/auth/forgot-password']);
  }

  showSuccessPopup(title: string, message: string): void {
    this.popupTitle = title;
    this.popupMessage = message;
    this.popupType = 'success';
    this.showPopup = true;
  }

  showErrorPopup(title: string, message: string): void {
    this.popupTitle = title;
    this.popupMessage = message;
    this.popupType = 'error';
    this.showPopup = true;
  }

  closePopup(): void {
    this.showPopup = false;
  }
}