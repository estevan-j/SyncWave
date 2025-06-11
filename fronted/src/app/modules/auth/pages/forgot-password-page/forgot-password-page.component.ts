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
      return;
    }

    this.loading = true;
    const email = this.emailForm.get('email')?.value;

    this.authService.verifyEmail(email).subscribe({
      next: (response: any) => {
        if (response.success) {
          this.verifiedEmail = email;
          this.step = 2;
          this.showSuccessPopup('Email verificado', 'Ahora puedes establecer tu nueva contraseña.');
        }
      },
      error: (error) => {
        if (error.status === 404) {
          this.showErrorPopup('Usuario no encontrado', 'No existe una cuenta con este correo electrónico.');
        } else {
          this.showErrorPopup('Error', 'Ocurrió un error al verificar el correo electrónico.');
        }
      },
      complete: () => {
        this.loading = false;
      }
    });
  }

  onSubmitReset(): void {
    if (this.resetForm.invalid) {
      return;
    }

    this.loading = true;
    const newPassword = this.resetForm.get('newPassword')?.value;

    this.authService.resetPassword(this.verifiedEmail, newPassword).subscribe({
      next: (response: any) => {
        if (response.success) {
          this.showSuccessPopup('Contraseña actualizada', 'Tu contraseña ha sido actualizada correctamente. Ahora puedes iniciar sesión.');
          setTimeout(() => {
            this.router.navigate(['/auth/login']);
          }, 2000);
        }
      },
      error: (error) => {
        this.showErrorPopup('Error', 'Ocurrió un error al actualizar la contraseña.');
      },
      complete: () => {
        this.loading = false;
      }
    });
  }

  goBackToEmail(): void {
    this.step = 1;
    this.resetForm.reset();
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