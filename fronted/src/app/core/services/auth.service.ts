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
        return this.apiService.post('/api/users', { email, password })
            .pipe(
                map((response: any) => {
                    if (response.success) {
                        this.userService.setCurrentUser(response.data);
                    }
                    return response;
                })
            );
    }

    login(email: string, password: string): Observable<any> {
        return this.apiService.post('/api/users/login', { email, password })
            .pipe(
                map((response: any) => {
                    if (response.success) {
                        this.userService.setCurrentUser(response.data);
                    }
                    return response;
                })
            );
    }

    logout(): void {
        this.userService.logout();
    }

    isAuthenticated(): boolean {
        return this.userService.isAuthenticated();
    } getCurrentUser(): any {
        return this.userService.getCurrentUser();
    }

    // Password recovery methods
    verifyEmail(email: string): Observable<any> {
        return this.apiService.post('/api/users/verify-email', { email });
    }

    resetPassword(email: string, newPassword: string): Observable<any> {
        return this.apiService.post('/api/users/reset-password', { email, newPassword });
    }
}
