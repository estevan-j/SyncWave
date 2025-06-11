import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-forgot-password-page',
  templateUrl: './forgot-password-page.component.html',
  styleUrls: ['./forgot-password-page.component.css']
})
export class ForgotPasswordPageComponent implements OnInit {
  forgotPasswordForm: FormGroup;
  loading = false;
  showPopup = false;
  popupTitle = '';
  popupMessage = '';
  popupType = 'success';

  constructor(
    private fb: FormBuilder,
    private router: Router
  ) {
    this.forgotPasswordForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]]
    });
  }

  ngOnInit(): void {}

  onSubmit(): void {
    if (this.forgotPasswordForm.invalid) {
      return;
    }

    this.loading = true;
    
    // Simular envío de correo (en una implementación real, llamarías a tu API)
    setTimeout(() => {
      this.showSuccessPopup(
        'Correo enviado', 
        'Hemos enviado un enlace para restablecer tu contraseña al correo electrónico proporcionado.'
      );
      this.loading = false;
    }, 1500);
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