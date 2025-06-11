import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { UserService } from '../../../../../../core/services/user.service';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../../../environments/environment';

@Component({
  selector: 'app-login-page',
  templateUrl: './login-page.component.html',
  styleUrls: ['./login-page.component.css']
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
    private http: HttpClient
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }

  ngOnInit(): void {
    // Verificar si ya está autenticado
    if (this.userService.isAuthenticated()) {
      this.router.navigate(['/home']);
    }
  }

  onLogin(): void {
    if (this.loginForm.invalid) {
      return;
    }

    this.loading = true;
    
    this.http.post(`${environment.apiUrl}/api/users/login`, this.loginForm.value)
      .subscribe({
        next: (response: any) => {
          this.userService.setCurrentUser(response.user);
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