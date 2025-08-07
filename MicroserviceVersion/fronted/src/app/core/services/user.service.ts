import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private currentUserSubject = new BehaviorSubject<any>(null);
  currentUser$ = this.currentUserSubject.asObservable();
  constructor() {
    // Intenta cargar el usuario desde localStorage al inicializar
    try {
      const user = localStorage.getItem('currentUser');
      if (user && user !== 'undefined' && user !== 'null') {
        const parsedUser = JSON.parse(user);
        this.currentUserSubject.next(parsedUser);
      }
    } catch (error) {
      console.warn('Error parsing user from localStorage:', error);
      localStorage.removeItem('currentUser');
    }
  }
  setCurrentUser(user: any): void {
    if (user) {
      localStorage.setItem('currentUser', JSON.stringify(user));
      this.currentUserSubject.next(user);
    } else {
      localStorage.removeItem('currentUser');
      this.currentUserSubject.next(null);
    }
  }

  getCurrentUser(): any {
    return this.currentUserSubject.value;
  }

  isAuthenticated(): boolean {
    return !!this.currentUserSubject.value;
  }

  logout(): void {
    localStorage.removeItem('currentUser');
    this.currentUserSubject.next(null);
  }
}