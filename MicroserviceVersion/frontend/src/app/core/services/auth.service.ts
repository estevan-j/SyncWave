import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { ApiService } from './api.service';
import { UserService } from './user.service';

@Injectable({
    providedIn: 'root'
})
export class AuthService {

    constructor(
        private apiService: ApiService,
        private userService: UserService
    ) { }

    register(email: string, password: string): Observable<any> {
        return this.apiService.post('/api/auth/signup', { email, password })
            .pipe(
                map((response: any) => {
                    if (response.access_token) {
                        this.setToken(response.access_token);
                        if (response.user) {
                            this.userService.setCurrentUser(response.user);
                        }
                    }
                    return response;
                })
            );
    }

    login(email: string, password: string): Observable<any> {
        return this.apiService.post('/api/auth/login', { email, password })
            .pipe(
                map((response: any) => {
                    if (response.access_token) {
                        this.setToken(response.access_token);
                        if (response.user) {
                            this.userService.setCurrentUser(response.user);
                        }
                    }
                    return response;
                })
            );
    }

    logout(): void {
        const token = this.getToken();
        if (token) {
            // Usar el método postWithAuth si existe, o modificar ApiService
            this.apiService.postWithAuth('/api/auth/logout', {}, token).subscribe({
                next: () => {
                    this.clearToken();
                    this.userService.logout();
                },
                error: () => {
                    // Aunque falle el logout en el servidor, limpiamos el token local
                    this.clearToken();
                    this.userService.logout();
                }
            });
        } else {
            this.userService.logout();
        }
    }

    isAuthenticated(): boolean {
        const token = this.getToken();
        return !!token && this.userService.isAuthenticated();
    }

    getCurrentUser(): any {
        return this.userService.getCurrentUser();
    }

    // Token management methods
    getToken(): string | null {
        return localStorage.getItem('access_token');
    }

    setToken(token: string): void {
        localStorage.setItem('access_token', token);
    }

    clearToken(): void {
        localStorage.removeItem('access_token');
    }

    // Password recovery methods
    verifyEmail(email: string): Observable<any> {
        return this.apiService.post('/api/auth/verify-email', { email });
    }

    resetPassword(email: string, newPassword: string): Observable<any> {
        return this.apiService.post('/api/auth/reset-password', {
            email,
            new_password: newPassword
        });
    }
}