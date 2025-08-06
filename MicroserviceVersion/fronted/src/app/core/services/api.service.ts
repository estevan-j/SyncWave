import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private readonly API_BASE_URL = 'http://localhost:5000'; // Ajusta esta URL según tu backend

  constructor(private http: HttpClient) { }

  post(endpoint: string, body: any) {
    return this.http.post(`${this.API_BASE_URL}${endpoint}`, body);
  }

  get(endpoint: string) {
    return this.http.get(`${this.API_BASE_URL}${endpoint}`);
  }

  put(endpoint: string, body: any) {
    return this.http.put(`${this.API_BASE_URL}${endpoint}`, body);
  }

  delete(endpoint: string) {
    return this.http.delete(`${this.API_BASE_URL}${endpoint}`);
  }

  // Método para peticiones POST autenticadas
  postWithAuth(endpoint: string, body: any, token: string) {
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });

    return this.http.post(`${this.API_BASE_URL}${endpoint}`, body, { headers });
  }

  // Método para peticiones GET autenticadas
  getWithAuth(endpoint: string, token: string) {
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    return this.http.get(`${this.API_BASE_URL}${endpoint}`, { headers });
  }

  // Método para peticiones PUT autenticadas
  putWithAuth(endpoint: string, body: any, token: string) {
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });

    return this.http.put(`${this.API_BASE_URL}${endpoint}`, body, { headers });
  }

  // Método para peticiones DELETE autenticadas
  deleteWithAuth(endpoint: string, token: string) {
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    return this.http.delete(`${this.API_BASE_URL}${endpoint}`, { headers });
  }
}