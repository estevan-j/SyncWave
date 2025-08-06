import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../../../core/services/auth.service';

@Component({
  selector: 'app-forgot-password-page',
  templateUrl: './forgot-password-page.component.html',
  styleUrls: ['./forgot-password-page.component.css'],
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule]
})
export class ForgotPasswordPageComponent implements OnInit {
  emailForm: FormGroup;
  resetForm: FormGroup;
  loading = false;
  showPopup = false;
  popupTitle = '';
  popupMessage = '';
  popupType = 'success';

  // Flow control
  step = 1; // 1: email verification, 2: password reset
  verifiedEmail = '';

  // Nuevos campos para mostrar errores de backend
  emailError: string | null = null;
  resetError: string | null = null;

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private authService: AuthService
  ) {
    this.emailForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]]
    });

    this.resetForm = this.fb.group({
      newPassword: ['', [Validators.required, Validators.minLength(6)]],
      confirmPassword: ['', [Validators.required]]
    }, { validator: this.passwordMatchValidator });
  }

  ngOnInit(): void { }

  passwordMatchValidator(formGroup: FormGroup) {
    const password = formGroup.get('newPassword')?.value;
    const confirmPassword = formGroup.get('confirmPassword')?.value;
    return password === confirmPassword ? null : { mismatch: true };
  }


  onSubmitEmail(): void {
    if (this.emailForm.invalid) {
      this.emailForm.markAllAsTouched();
      return;
    }

    this.loading = true;
    this.emailError = null;

    const email = this.emailForm.get('email')?.value;

    this.authService.verifyEmail(email).subscribe({
      next: (response: any) => {
        // Verificar si el email existe
        if (response.email_exists === true) {
          this.verifiedEmail = email;
          this.step = 2;
          this.showSuccessPopup('Email verificado', 'Ahora puedes establecer tu nueva contraseña.');
        } else if (response.email_exists === false) {
          this.emailError = 'Este correo electrónico no está registrado en nuestro sistema.';
          this.showErrorPopup('Email no encontrado', 'Este correo electrónico no está registrado en nuestro sistema.');
        } else {
          // Fallback para respuestas con formato diferente
          this.emailError = 'Respuesta inesperada del servidor.';
          this.showErrorPopup('Error', 'Respuesta inesperada del servidor.');
        }
      },
      error: (error) => {
        if (error.status === 404) {
          this.emailError = 'Este correo electrónico no está registrado en nuestro sistema.';
          this.showErrorPopup('Email no encontrado', this.emailError ?? '');
        } else if (error.error && error.error.message) {
          this.emailError = error.error.message;
          this.showErrorPopup('Error', this.emailError ?? ''); // Usar ?? para manejar null
        } else {
          this.emailError = 'Ocurrió un error al verificar el correo electrónico.';
          this.showErrorPopup('Error', this.emailError ?? '');
        }
      },
      complete: () => {
        this.loading = false;
      }
    });
  }


  onSubmitReset(): void {
    if (this.resetForm.invalid) {
      this.resetForm.markAllAsTouched();
      return;
    }

    this.loading = true;
    this.resetError = null;

    const newPassword = this.resetForm.get('newPassword')?.value;

    this.authService.resetPassword(this.verifiedEmail, newPassword).subscribe({
      next: (response: any) => {
        if (response.success) {
          this.showSuccessPopup('Contraseña actualizada', 'Tu contraseña ha sido actualizada correctamente. Redirigiendo al login...');
          // Mantener loading = true durante la redirección
          setTimeout(() => {
            this.router.navigate(['/auth/login']);
          }, 2000);
        } else {
          this.loading = false;
        }
      },
      error: (error) => {
        if (error.error && error.error.message) {
          this.resetError = error.error.message;
          this.showErrorPopup('Error', this.resetError ?? '');
        } else {
          this.resetError = 'Ocurrió un error al actualizar la contraseña.';
          this.showErrorPopup('Error', this.resetError ?? '');
        }
        this.loading = false;
      }
    });
  }

  goBackToEmail(): void {
    this.step = 1;
    this.resetForm.reset();
    this.resetError = null;
    this.emailError = null; // Limpiar error del email también
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