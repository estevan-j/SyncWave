import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../../../core/services/auth.service'; // Cambia ApiService por AuthService

@Component({
  selector: 'app-register-page',
  templateUrl: './register-page.component.html',
  styleUrls: ['./register-page.component.css'],
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule]
})
export class RegisterPageComponent implements OnInit {
  registerForm: FormGroup;
  loading = false;
  showPopup = false;
  popupTitle = '';
  popupMessage = '';
  popupType = 'success';

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private authService: AuthService // Usa AuthService
  ) {
    this.registerForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      confirmPassword: ['', [Validators.required]]
    }, { validator: this.passwordMatchValidator });
  }

  ngOnInit(): void { }

  passwordMatchValidator(formGroup: FormGroup) {
    const password = formGroup.get('password')?.value;
    const confirmPassword = formGroup.get('confirmPassword')?.value;
    return password === confirmPassword ? null : { mismatch: true };
  }

  onRegister(): void {
    if (this.registerForm.invalid) {
      return;
    }

    this.loading = true;

    const { email, password } = this.registerForm.value;

    this.authService.register(email, password)
      .subscribe({
        next: (response: any) => {
          this.showSuccessPopup('Registro exitoso', 'Tu cuenta ha sido creada correctamente. Ahora puedes iniciar sesión.');
          setTimeout(() => {
            this.router.navigate(['/auth/login']);
          }, 1500);
        },
        error: (error) => {
          if (error.status === 400 && error.error.message === 'Email already exists') {
            this.showErrorPopup('Error de registro', 'Este correo electrónico ya está en uso');
          } else {
            this.showErrorPopup('Error', 'Ocurrió un error al intentar registrarte');
          }
          this.loading = false;
        },
        complete: () => {
          this.loading = false;
        }
      });
  }

  goToLogin(): void {
    this.router.navigate(['/auth/login']);
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